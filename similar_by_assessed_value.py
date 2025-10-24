"""Display similar properties sorted by AVM value"""
import requests
import pandas as pd

url = "http://localhost:5001/property/similar"

test_data = {
    "street": "4 Fiorenza Drive",
    "city": "Wilmington",
    "county": "",
    "state": "MA",
    "zip_code": "01887",
    "sqft_tolerance": 10.0,
    "radius_miles": 5.0
}

print("=" * 160)
print("SIMILAR PROPERTIES WITH AVM & ASSESSED VALUES (Sorted by AVM Value)")
print("=" * 160)

try:
    response = requests.post(url, json=test_data, timeout=120)

    if response.status_code == 200:
        data = response.json()

        # Show subject property
        subject = data.get('subject_property', {})
        print(f"\nSUBJECT PROPERTY: {subject.get('address')}")
        print(f"  Beds: {subject.get('bedrooms')} | Baths: {subject.get('bathrooms')} | SqFt: {subject.get('sqft'):,}")

        # Show filters
        filters = data.get('filters_applied', {})
        print(f"\nFILTERS: {filters.get('bedrooms')} beds, {filters.get('bathrooms')} baths, {filters.get('sqft_range')} sqft ({filters.get('sqft_tolerance')}), {filters.get('radius_miles')} miles")

        # Convert to DataFrame
        comparables = data.get('comparables', [])

        if comparables:
            # Create DataFrame
            df = pd.DataFrame(comparables)

            # Sort by raw_avm_value descending
            df = df.sort_values('raw_avm_value', ascending=False)

            # Reorder columns for display
            column_order = [
                'avm_value',
                'assessed_value',
                'avm_per_sqft',
                'assessed_per_sqft',
                'confidence_score',
                'avm_value_low',
                'avm_value_high',
                'address',
                'distance_miles',
                'bedrooms',
                'bathrooms',
                'building_size_sqft',
                'year_built',
                'event_date',
                'raw_avm_value',
                'raw_assessed_value'
            ]

            # Only include columns that exist
            display_columns = [col for col in column_order if col in df.columns]
            df_display = df[display_columns].copy()

            # Rename columns
            df_display = df_display.rename(columns={
                'avm_value': 'AVM Value',
                'assessed_value': 'Assessed Value',
                'avm_per_sqft': 'AVM $/SqFt',
                'assessed_per_sqft': 'Assessed $/SqFt',
                'confidence_score': 'Confidence',
                'avm_value_low': 'Low Estimate',
                'avm_value_high': 'High Estimate',
                'address': 'Address',
                'distance_miles': 'Distance (mi)',
                'bedrooms': 'Beds',
                'bathrooms': 'Baths',
                'building_size_sqft': 'SqFt',
                'year_built': 'Built',
                'event_date': 'Event Date',
                'raw_avm_value': 'Raw AVM $',
                'raw_assessed_value': 'Raw Assessed $'
            })

            print(f"\n{len(df_display)} COMPARABLE PROPERTIES (Sorted by AVM Value - Highest to Lowest)")
            print("=" * 160)

            # Display DataFrame
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', 45)

            print(df_display.to_string(index=True))

            # Show statistics
            print("\n" + "=" * 160)
            print("VALUE COMPARISON STATISTICS")
            print("=" * 160)

            avm_values = df[df['raw_avm_value'] > 0]['raw_avm_value']
            assessed_values = df[df['raw_assessed_value'] > 0]['raw_assessed_value']

            if len(avm_values) > 0:
                print(f"\nAVM VALUES:")
                print(f"   Properties with AVM data: {len(avm_values)} out of {len(df)}")
                print(f"   Minimum AVM Value: ${avm_values.min():,.2f}")
                print(f"   Maximum AVM Value: ${avm_values.max():,.2f}")
                print(f"   Average AVM Value: ${avm_values.mean():,.2f}")
                print(f"   Median AVM Value: ${avm_values.median():,.2f}")
                print(f"   Std Deviation: ${avm_values.std():,.2f}")

                # Show confidence score stats
                confidence_scores = df[df['confidence_score'] > 0]['confidence_score']
                if len(confidence_scores) > 0:
                    print(f"\nCONFIDENCE SCORES:")
                    print(f"   Average Confidence Score: {confidence_scores.mean():.1f}/100")
                    print(f"   Min Confidence Score: {confidence_scores.min()}/100")
                    print(f"   Max Confidence Score: {confidence_scores.max()}/100")
            else:
                print("\nNo AVM values available")

            if len(assessed_values) > 0:
                print(f"\nASSESSED VALUES:")
                print(f"   Properties with assessed data: {len(assessed_values)} out of {len(df)}")
                print(f"   Minimum Assessed Value: ${assessed_values.min():,.2f}")
                print(f"   Maximum Assessed Value: ${assessed_values.max():,.2f}")
                print(f"   Average Assessed Value: ${assessed_values.mean():,.2f}")
                print(f"   Median Assessed Value: ${assessed_values.median():,.2f}")
                print(f"   Std Deviation: ${assessed_values.std():,.2f}")

                # Calculate difference between AVM and assessed
                if len(avm_values) > 0 and len(avm_values) == len(assessed_values):
                    diff = avm_values.values - assessed_values.values
                    avg_diff = diff.mean()
                    avg_pct_diff = (diff / assessed_values.values * 100).mean()
                    print(f"\nAVM vs ASSESSED COMPARISON:")
                    print(f"   Average Difference: ${avg_diff:,.2f}")
                    print(f"   Average % Difference: {avg_pct_diff:,.1f}%")
                    print(f"   AVM Higher Than Assessed: {(diff > 0).sum()} properties")
                    print(f"   AVM Lower Than Assessed: {(diff < 0).sum()} properties")

        else:
            print("\nNo comparable properties found")

    else:
        print(f"\nError {response.status_code}: {response.text}")

except Exception as e:
    print(f"\nException: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 120)
