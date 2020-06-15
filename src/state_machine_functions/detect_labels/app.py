import os
import json
import boto3
import requests

client = boto3.client('rekognition', region_name=os.environ['AWS_REGION'])

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

    # NOTE: Shopify product may have up to 250 images
    # NOTE: Images can be in PNG or GIF or JPG
    images = event['images']
    tag_tracker = set([x.lower() for x in existing_tags])
    new_tags = set()
    for image in images:
        print(f"Working on image {image['position']}")
        image_response = requests.get(image['src'])
        # TODO: Need to ensure it's PNG or JPG
        # TODO: Need to ensure it's 5MB or smaller OR use S3 bucket
        # NOTE: Default confidence is 55%
        response = client.detect_labels(Image={'Bytes': image_response.content}, MinConfidence=float(95))
        labels = [sub['Name'] for sub in response['Labels']]
        print(f"Labels detected: {labels}")
        for label in labels:
            if label.lower() not in tag_tracker:
                tag_tracker.add(label.lower())
                new_tags.add(label)

    print(f"New tags: {new_tags}")

    if len(new_tags) == 0:
        print("No new tags/labels detected.")

    return {
        'shop_domain': shop_domain,
        'product_id': product_id,
        'existing_tags': list(existing_tags),
        'new_tags': list(new_tags),
        'new_tags_count': len(new_tags)
    }
