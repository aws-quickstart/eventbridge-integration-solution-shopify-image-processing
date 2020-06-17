import os
import json
import requests

API_VERSION = '2020-04'

def lambda_handler(event, context):
    print(f"Event Received:\n{json.dumps(event)}")

    shop_domain = event['shop_domain']
    print(f"Shop Domain: {shop_domain}")

    # NOTE: Shopify product ID is an unsigned 64-bit integer that's used as a
    # unique identifier for the product. Each id is unique across the Shopify
    # system. No two products will have the same id, even if they're from
    # different shops.
    product_id = event['product_id']
    print(f"Product ID: {product_id}")

    # NOTE: Shopify limits tags to 250
    # NOTE: Each tag can have up to 255 characters
    existing_tags = set(event['existing_tags'])
    print(f"Existing tags: {existing_tags}")
    new_tags = set(event['new_tags'])
    print(f"New tags: {new_tags}")

    # NOTE: Shopify limits tags to 250
    # NOTE: Each tag can have up to 255 characters
    # NOTE: Tags are stored comma+space separated

    combined_tags = existing_tags.union(new_tags)
    print(f"Combined tags: {combined_tags}")

    print("Updating tags...")
    # NOTE: This is where you could do an access_token lookup for multiple shops
    # based on the Shopify shop domain of the merchant. In this example, we
    # just use the access_token that was provided as part of the function configuration.
    access_token = os.environ['access_token']

    headers = {
        'Content-Type': "application/json",
        'X-Shopify-Access-Token': access_token
    }
    body = {
        'product': {
            'id': product_id,
            'tags': ', '.join(combined_tags)
        }
    }
    response = requests.put(
        url=f"https://{shop_domain}/admin/api/{API_VERSION}/products/{product_id}.json",
        json=body,
        headers=headers)

    print(f"Response:\n{json.dumps(response.json())}")
