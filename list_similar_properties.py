"""List similar properties with sale data in a clean format"""
import requests

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
print("SIMILAR PROPERTIES LIST - 15 CLOSEST WITH SALE DATA")
print("=" * 100)

try:
    response = requests.post(url, json=test_data, timeout=120)

    if response.status_code == 200:
        data = response.json()

        # Show subject property
        subject = data.get('subject_property', {})
        print(f"\nSUBJECT PROPERTY:")
        print(f"  {subject.get('address')}")
        print(f"  {subject.get('bedrooms')} beds | {subject.get('bathrooms')} baths | {subject.get('sqft'):,} sqft")

        # Show comparables
        comparables = data.get('comparables', [])

        if comparables:
            print(f"\n{len(comparables)} COMPARABLE PROPERTIES (sorted by distance):")
            print("=" * 100)

            for i, prop in enumerate(comparables, 1):
                print(f"\n{i}. {prop.get('address')}")
                print(f"   Distance: {prop.get('distance_miles')} mi | {prop.get('bedrooms')} bed | {prop.get('bathrooms')} bath | {prop.get('building_size_sqft'):,} sqft | Built: {prop.get('year_built')}")
                print(f"   Sale: {prop.get('sale_price')} | Date: {prop.get('sale_date')} | Price/SqFt: {prop.get('price_per_sqft')}")

        else:
            print("\nNo comparable properties found")

    else:
        print(f"\nError {response.status_code}: {response.text}")

except Exception as e:
    print(f"\nException: {str(e)}")

print("\n" + "=" * 100)
