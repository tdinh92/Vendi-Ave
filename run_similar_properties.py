"""Simple wrapper to run similar properties analysis"""
from property_api_service import PropertyAPIService

service = PropertyAPIService()

print("=" * 100)
print("SIMILAR PROPERTIES WITH ASSESSMENT DATA")
print("=" * 100)

address = input("\nEnter property address: ").strip()

if not address:
    print("No address provided")
    exit()

print(f"\nParsing address: {address}")

# Parse address
addr_parts = service.parse_address(address)
street = addr_parts.get('street', '')
city = addr_parts.get('city', '')
state = addr_parts.get('state', '')
zip_code = addr_parts.get('zip', '')
county = ''

print(f"Street: {street}")
print(f"City: {city}")
print(f"State: {state}")
print(f"ZIP: {zip_code}")

print("\nFinding similar properties with assessment data...")

# Get similar properties
report = service.get_similar_properties_with_sales(street, city, county, state, zip_code)

# Display results
print("\n" + "=" * 100)
print("RESULTS")
print("=" * 100)

if 'error' in report:
    print(f"\nError: {report['error']}")
else:
    # Show subject property
    if 'subject_property' in report:
        subject = report['subject_property']
        print(f"\nSUBJECT PROPERTY:")
        print(f"  Address: {subject.get('address', 'N/A')}")
        print(f"  Bedrooms: {subject.get('bedrooms', 'N/A')}")
        print(f"  Bathrooms: {subject.get('bathrooms', 'N/A')}")
        if subject.get('sqft'):
            print(f"  Square Feet: {subject.get('sqft'):,}")

    # Show filters
    if 'filters_applied' in report:
        filters = report['filters_applied']
        print(f"\nFILTERS APPLIED:")
        print(f"  Bedrooms: {filters.get('bedrooms', 'N/A')}")
        print(f"  Bathrooms: {filters.get('bathrooms', 'N/A')}")
        print(f"  Sqft Range: {filters.get('sqft_range', 'N/A')} ({filters.get('sqft_tolerance', 'N/A')})")
        print(f"  Radius: {filters.get('radius_miles', 'N/A')} miles")

    total_comps = report.get('total_comparables', 0)
    print(f"\nFOUND {total_comps} SIMILAR PROPERTIES (15 CLOSEST)")
    print("=" * 100)

    if total_comps > 0:
        comparables = report.get('comparables', [])

        for i, comp in enumerate(comparables, 1):
            print(f"\nPROPERTY #{i}")
            print(f"  Address: {comp.get('address', 'N/A')}")
            print(f"  Distance: {comp.get('distance_miles', 'N/A')} miles")
            print(f"  Beds/Baths: {comp.get('bedrooms', 'N/A')}/{comp.get('bathrooms', 'N/A')}")
            print(f"  Size: {comp.get('building_size_sqft', 'N/A')} sq ft")
            print(f"  Year Built: {comp.get('year_built', 'N/A')}")
            print(f"  Assessed Value: {comp.get('total_assessed_value', 'N/A')} (Tax Year: {comp.get('tax_year', 'N/A')})")
            print(f"  Tax Amount: {comp.get('tax_amount', 'N/A')}")
            print(f"  Last Sale: {comp.get('sale_price', 'N/A')} ({comp.get('sale_date', 'N/A')})")
            print(f"  Price/SqFt: {comp.get('price_per_sqft', 'N/A')}")

print(f"\nData retrieved: {report.get('data_retrieved', 'N/A')}")
print("\n" + "=" * 100)
