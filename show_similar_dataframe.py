"""Display similar properties with sale data as a pandas DataFrame"""
import requests
import pandas as pd
import json

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

print("=" * 100)
print("SIMILAR PROPERTIES WITH SALE DATA - DATAFRAME VIEW")
print("=" * 100)

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
            # Create DataFrame with selected columns
            df = pd.DataFrame(comparables)

            # Reorder columns for better display
            column_order = [
                'distance_miles',
                'address',
                'bedrooms',
                'bathrooms',
                'building_size_sqft',
                'year_built',
                'sale_price',
                'sale_date',
                'price_per_sqft',
                'raw_sale_price'
            ]

            # Only include columns that exist
            display_columns = [col for col in column_order if col in df.columns]
            df = df[display_columns]

            # Rename columns for better readability
            df = df.rename(columns={
                'distance_miles': 'Distance (mi)',
                'address': 'Address',
                'bedrooms': 'Beds',
                'bathrooms': 'Baths',
                'building_size_sqft': 'SqFt',
                'year_built': 'Year Built',
                'sale_price': 'Sale Price',
                'sale_date': 'Sale Date',
                'price_per_sqft': '$/SqFt',
                'raw_sale_price': 'Raw Sale $'
            })

            print(f"\n{len(df)} COMPARABLE PROPERTIES FOUND")
            print("=" * 100)

            # Display full DataFrame
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', 50)

            print(df.to_string(index=True))

            # Show statistics on raw sale prices (excluding 0 values)
            print("\n" + "=" * 100)
            print("SALE PRICE STATISTICS (Properties with disclosed sales)")
            print("=" * 100)

            disclosed_sales = df[df['Raw Sale $'] > 0]['Raw Sale $']

            if len(disclosed_sales) > 0:
                print(f"\nNumber of properties with disclosed sales: {len(disclosed_sales)} out of {len(df)}")
                print(f"Minimum Sale Price: ${disclosed_sales.min():,.2f}")
                print(f"Maximum Sale Price: ${disclosed_sales.max():,.2f}")
                print(f"Average Sale Price: ${disclosed_sales.mean():,.2f}")
                print(f"Median Sale Price: ${disclosed_sales.median():,.2f}")
                print(f"Std Deviation: ${disclosed_sales.std():,.2f}")
            else:
                print("\nNo disclosed sale prices available")

            # Show distance distribution
            print("\n" + "=" * 100)
            print("DISTANCE DISTRIBUTION")
            print("=" * 100)
            print(f"\nClosest property: {df['Distance (mi)'].min()} miles")
            print(f"Farthest property: {df['Distance (mi)'].max()} miles")
            print(f"Average distance: {df['Distance (mi)'].mean():.2f} miles")

            # Show properties by distance ranges
            print("\nProperties by Distance:")
            print(f"  0.0 - 0.5 miles: {len(df[df['Distance (mi)'] <= 0.5])} properties")
            print(f"  0.5 - 1.0 miles: {len(df[(df['Distance (mi)'] > 0.5) & (df['Distance (mi)'] <= 1.0)])} properties")
            print(f"  1.0 - 1.5 miles: {len(df[(df['Distance (mi)'] > 1.0) & (df['Distance (mi)'] <= 1.5)])} properties")

        else:
            print("\nNo comparable properties found")

    else:
        print(f"\nError {response.status_code}: {response.text}")

except Exception as e:
    print(f"\nException: {str(e)}")

print("\n" + "=" * 100)
