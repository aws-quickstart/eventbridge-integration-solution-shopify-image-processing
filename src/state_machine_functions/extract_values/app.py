import json
from datetime import datetime
from datetime import timedelta

def lambda_handler(event, context):
    print(f"Event Received:\n{json.dumps(event)}")

    # NOTE: Ensure that images were actually updated vs. other product update
    # by ensuring that the updated_at timestamp for the product isn't more recent (delta > 0)
    # than the images timestamps
    image_updated = False
    images = []
    product_updated_at = datetime.fromisoformat(event['detail']['payload']['updated_at'])
    for image in event['detail']['payload']['images']:
        image_updated_at = datetime.fromisoformat(image['updated_at'])
        if not (product_updated_at - image_updated_at) > timedelta(0):
            image_updated = True
            images.append(image)

    # Exit early, if possible
    if not image_updated:
        print("No image was updated. Exiting.")
        return {
            'image_updated': image_updated
        }

    shop_domain = event['detail']['metadata']['X-Shopify-Shop-Domain']
    print(f"Shop Domain: {shop_domain}")

    # NOTE: Shopify product ID is an unsigned 64-bit integer that's used as a
    # unique identifier for the product. Each id is unique across the Shopify
    # system. No two products will have the same id, even if they're from
    # different shops.
    product_id = event['detail']['payload']['id']
    print(f"Product ID: {product_id}")

    # NOTE: Shopify limits tags to 250
    # NOTE: Each tag can have up to 255 characters
    # NOTE: Tags are stored comma+space separated
    existing_tags_string = event['detail']['payload']['tags']
    existing_tags = existing_tags_string.split(', ') if existing_tags_string else []
    print(f"Existing tags: {existing_tags}")

    # NOTE: Shopify product may have up to 250 images
    # NOTE: Images can be in PNG or GIF or JPG
    images_src = [sub['src'] for sub in event['detail']['payload']['images']]

    return {
        'shop_domain': shop_domain,
        'product_id': product_id,
        'existing_tags': existing_tags,
        'images': images,
        'image_updated': image_updated
    }

