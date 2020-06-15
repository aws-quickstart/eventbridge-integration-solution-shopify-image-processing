import sys
sys.path.append('../../state_machine_functions/')
sys.path.append('src/state_machine_functions/')

import os
import json
import unittest
from unittest import mock
from dataclasses import dataclass

from extract_values.app import lambda_handler as extract_values_handler
with mock.patch.dict('os.environ', {'AWS_REGION': 'us-west-2'}):
    from detect_labels.app import lambda_handler as detect_labels_handler
with mock.patch.dict('os.environ', {'access_token': '1234567890'}):
    from update_tags.app import lambda_handler as update_tags_handler


def mocked_client_detect_labels_call(self, operation_name, **kwarg):
    return {
        'Labels': [
            {
                'Name': "MockTag1"
            },
            {
                'Name': "MockTag2"
            }
        ]
    }

@dataclass
class MockRequestsResponse:
    def json(self, ):
        return {
            'Message': 'Mocked Success'
        }

def mocked_requests_put_call(url, json, headers):
    return MockRequestsResponse()


class ShopifyExtractValuesTest(unittest.TestCase):
    def test_image_updated(self,):
        print("\n\n*** Test test_image_updated ***")
        event_type = 'extract_values_image_updated'
        response = extract_values_handler(get_eventbridge_event(event_type), '')

        self.assertIn('shop_domain', response)
        self.assertIn('product_id', response)
        self.assertIn('existing_tags', response)
        self.assertIn('images', response)
        self.assertIn('image_updated', response)
        self.assertIsInstance(response['product_id'], int)
        self.assertIsInstance(response['existing_tags'],list)
        self.assertIsInstance(response['images'], list)
        self.assertIsInstance(response['image_updated'], bool)
        self.assertIs(response['image_updated'], True)

    def test_no_image_updated(self,):
        print("\n\n*** Test test_no_image_updated ***")
        event_type = 'extract_values_no_image_updated'
        response = extract_values_handler(get_eventbridge_event(event_type), '')

        self.assertIsInstance(response['image_updated'], bool)
        self.assertIs(response['image_updated'], False)


class ShopifyDetectLabelsTest(unittest.TestCase):
    @mock.patch('botocore.client.BaseClient._make_api_call', side_effect=mocked_client_detect_labels_call)
    def test_detect_labels(self, call_detect_labels_mock):
        print("\n\n*** Test test_detect_labels ***")
        event_type = 'detect_labels'
        response = detect_labels_handler(get_eventbridge_event(event_type), '')

        self.assertIn('shop_domain', response)
        self.assertIn('product_id', response)
        self.assertIn('existing_tags', response)
        self.assertIn('new_tags', response)
        self.assertIn('new_tags_count', response)
        self.assertIsInstance(response['product_id'], int)
        self.assertIsInstance(response['existing_tags'], list)
        self.assertIsInstance(response['new_tags'], list)
        self.assertIsInstance(response['new_tags_count'], int)
        # NOTE: Assuming test event has 4 images
        self.assertEqual(call_detect_labels_mock.call_count, 4)

class ShopifyUpdateTagsTest(unittest.TestCase):
    @mock.patch.dict('os.environ', {'access_token': '1234567890'})
    @mock.patch('requests.put', side_effect=mocked_requests_put_call)
    def test_update_tags(self, call_requests_mock):
        print("\n\n*** Test test_update_tags ***")
        assert 'access_token' in os.environ

        event_type = 'update_tags'
        response = update_tags_handler(get_eventbridge_event(event_type), '')

        self.assertEqual(call_requests_mock.call_count, 1)

def get_eventbridge_event(event_type):
    if event_type == 'extract_values_image_updated':
        return {
            "version": "0",
            "id": "0",
            "detail-type": "shopifyWebhook",
            "source": "aws.partner/shopify.com/0000000/aws-shopify-webhooks-test",
            "account": "000000000000",
            "time": "2020-06-10T22:02:31Z",
            "region": "us-west-2",
            "resources": [],
            "detail": {
                "payload": {
                    "id": 123456789,
                    "title": "test product",
                    "body_html": "<p>The best product in the world!</p>",
                    "vendor": "test shop",
                    "product_type": "",
                    "created_at": "2020-06-04T13:01:41-04:00",
                    "handle": "test-product",
                    "updated_at": "2020-06-10T18:07:46-04:00",
                    "published_at": "2020-06-04T12:58:43-04:00",
                    "template_suffix": "",
                    "published_scope": "web",
                    "tags": "Foo, Bar",
                    "admin_graphql_api_id": "gid://shopify/Product/123456789",
                    "variants": [
                        {
                            "id": 1234,
                            "product_id": 123456789,
                            "title": "Default Title",
                            "price": "0.00",
                            "sku": "",
                            "position": 1,
                            "inventory_policy": "deny",
                            "compare_at_price": None,
                            "fulfillment_service": "manual",
                            "inventory_management": "shopify",
                            "option1": "Default Title",
                            "option2": None,
                            "option3": None,
                            "created_at": "2020-06-04T13:01:41-04:00",
                            "updated_at": "2020-06-10T17:57:21-04:00",
                            "taxable": True,
                            "barcode": "",
                            "grams": 0,
                            "image_id": None,
                            "weight": 0,
                            "weight_unit": "lb",
                            "inventory_item_id": 123456,
                            "inventory_quantity": 0,
                            "old_inventory_quantity": 0,
                            "requires_shipping": True,
                            "admin_graphql_api_id": "gid://shopify/ProductVariant/1234"
                        }
                    ],
                    "options": [
                        {
                            "id": 6002644222001,
                            "product_id": 4656811540529,
                            "name": "Title",
                            "position": 1,
                            "values": [
                                "Default Title"
                            ]
                        }
                    ],
                    "images": [
                        {
                            "id": 123,
                            "product_id": 123456789,
                            "position": 1,
                            "created_at": "2020-06-04T14:52:09-04:00",
                            "updated_at": "2020-06-10T17:58:28-04:00",
                            "alt": None,
                            "width": 800,
                            "height": 441,
                            "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/abc.png?v=87654321",
                            "variant_ids": [],
                            "admin_graphql_api_id": "gid://shopify/ProductImage/123"
                        },
                        {
                            "id": 456,
                            "product_id": 123456789,
                            "position": 2,
                            "created_at": "2020-06-04T14:53:25-04:00",
                            "updated_at": "2020-06-10T17:58:28-04:00",
                            "alt": None,
                            "width": 2973,
                            "height": 4460,
                            "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/def.png?v=87654321",
                            "variant_ids": [],
                            "admin_graphql_api_id": "gid://shopify/ProductImage/456"
                        },
                        {
                            "id": 789,
                            "product_id": 123456789,
                            "position": 3,
                            "created_at": "2020-06-04T14:53:32-04:00",
                            "updated_at": "2020-06-10T17:58:28-04:00",
                            "alt": None,
                            "width": 2973,
                            "height": 4460,
                            "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/ghi.png?v=87654321",
                            "variant_ids": [],
                            "admin_graphql_api_id": "gid://shopify/ProductImage/789"
                        },
                        {
                            "id": 987,
                            "product_id": 123456789,
                            "position": 4,
                            "created_at": "2020-06-10T18:02:03-04:00",
                            "updated_at": "2020-06-10T18:07:46-04:00",
                            "alt": None,
                            "width": 2973,
                            "height": 4460,
                            "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/jkl.png?v=87654321",
                            "variant_ids": [],
                            "admin_graphql_api_id": "gid://shopify/ProductImage/987"
                        }
                    ],
                    "image": {
                        "id": 123,
                        "product_id": 123456789,
                        "position": 1,
                        "created_at": "2020-06-04T14:52:09-04:00",
                        "updated_at": "2020-06-10T17:58:28-04:00",
                        "alt": None,
                        "width": 800,
                        "height": 441,
                        "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/abc.png?v=87654321",
                        "variant_ids": [],
                        "admin_graphql_api_id": "gid://shopify/ProductImage/123"
                    }
                },
                "metadata": {
                    "Content-Type": "application/json",
                    "X-Shopify-Topic": "products/update",
                    "X-Shopify-Shop-Domain": "example.myshopify.com",
                    "X-Shopify-Product-Id": "123456789",
                    "X-Shopify-Hmac-SHA256": "DkXXXXX92/LQYUVHXXXXXXXXXXXXXXXXXXXXXXXXXfY=",
                    "X-Shopify-API-Version": "unstable"
                }
            }
        }
    elif event_type == 'extract_values_no_image_updated':
        return {
            "version": "0",
            "id": "0",
            "detail-type": "shopifyWebhook",
            "source": "aws.partner/shopify.com/0000000/aws-shopify-webhooks-test",
            "account": "000000000000",
            "time": "2020-06-10T22:02:31Z",
            "region": "us-west-2",
            "resources": [],
            "detail": {
                "payload": {
                    "id": 123456789,
                    "title": "test product",
                    "body_html": "<p>The best product in the world!</p>",
                    "vendor": "test shop",
                    "product_type": "",
                    "created_at": "2020-06-04T13:01:41-04:00",
                    "handle": "test-product",
                    "updated_at": "2020-06-10T18:02:20-04:00",
                    "published_at": "2020-06-04T12:58:43-04:00",
                    "template_suffix": "",
                    "published_scope": "web",
                    "tags": "Foo, Bar",
                    "admin_graphql_api_id": "gid://shopify/Product/123456789",
                    "variants": [
                        {
                            "id": 1234,
                            "product_id": 123456789,
                            "title": "Default Title",
                            "price": "0.00",
                            "sku": "",
                            "position": 1,
                            "inventory_policy": "deny",
                            "compare_at_price": None,
                            "fulfillment_service": "manual",
                            "inventory_management": "shopify",
                            "option1": "Default Title",
                            "option2": None,
                            "option3": None,
                            "created_at": "2020-06-04T13:01:41-04:00",
                            "updated_at": "2020-06-10T17:57:21-04:00",
                            "taxable": True,
                            "barcode": "",
                            "grams": 0,
                            "image_id": None,
                            "weight": 0,
                            "weight_unit": "lb",
                            "inventory_item_id": 123456,
                            "inventory_quantity": 0,
                            "old_inventory_quantity": 0,
                            "requires_shipping": True,
                            "admin_graphql_api_id": "gid://shopify/ProductVariant/1234"
                        }
                    ],
                    "options": [
                        {
                            "id": 6002644222001,
                            "product_id": 4656811540529,
                            "name": "Title",
                            "position": 1,
                            "values": [
                                "Default Title"
                            ]
                        }
                    ],
                    "images": [
                        {
                            "id": 123,
                            "product_id": 123456789,
                            "position": 1,
                            "created_at": "2020-06-04T14:52:09-04:00",
                            "updated_at": "2020-06-10T17:58:28-04:00",
                            "alt": None,
                            "width": 800,
                            "height": 441,
                            "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/abc.png?v=87654321",
                            "variant_ids": [],
                            "admin_graphql_api_id": "gid://shopify/ProductImage/123"
                        },
                        {
                            "id": 456,
                            "product_id": 123456789,
                            "position": 2,
                            "created_at": "2020-06-04T14:53:25-04:00",
                            "updated_at": "2020-06-10T17:58:28-04:00",
                            "alt": None,
                            "width": 2973,
                            "height": 4460,
                            "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/def.png?v=87654321",
                            "variant_ids": [],
                            "admin_graphql_api_id": "gid://shopify/ProductImage/456"
                        },
                        {
                            "id": 789,
                            "product_id": 123456789,
                            "position": 3,
                            "created_at": "2020-06-04T14:53:32-04:00",
                            "updated_at": "2020-06-10T17:58:28-04:00",
                            "alt": None,
                            "width": 2973,
                            "height": 4460,
                            "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/ghi.png?v=87654321",
                            "variant_ids": [],
                            "admin_graphql_api_id": "gid://shopify/ProductImage/789"
                        },
                        {
                            "id": 987,
                            "product_id": 123456789,
                            "position": 4,
                            "created_at": "2020-06-10T18:02:03-04:00",
                            "updated_at": "2020-06-10T18:02:03-04:00",
                            "alt": None,
                            "width": 2973,
                            "height": 4460,
                            "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/jkl.png?v=87654321",
                            "variant_ids": [],
                            "admin_graphql_api_id": "gid://shopify/ProductImage/987"
                        }
                    ],
                    "image": {
                        "id": 123,
                        "product_id": 123456789,
                        "position": 1,
                        "created_at": "2020-06-04T14:52:09-04:00",
                        "updated_at": "2020-06-10T17:58:28-04:00",
                        "alt": None,
                        "width": 800,
                        "height": 441,
                        "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/abc.png?v=87654321",
                        "variant_ids": [],
                        "admin_graphql_api_id": "gid://shopify/ProductImage/123"
                    }
                },
                "metadata": {
                    "Content-Type": "application/json",
                    "X-Shopify-Topic": "products/update",
                    "X-Shopify-Shop-Domain": "example.myshopify.com",
                    "X-Shopify-Product-Id": "123456789",
                    "X-Shopify-Hmac-SHA256": "DkXXXXX92/LQYUVHXXXXXXXXXXXXXXXXXXXXXXXXXfY=",
                    "X-Shopify-API-Version": "unstable"
                }
            }
        }
    elif event_type == 'detect_labels':
        return {
            'shop_domain': "example.myshopify.com",
            'product_id': 123456789,
            'existing_tags': ['Foo', 'Bar'],
            'images': [
                {
                    "id": 123,
                    "product_id": 123456789,
                    "position": 1,
                    "created_at": "2020-06-04T14:52:09-04:00",
                    "updated_at": "2020-06-10T17:58:28-04:00",
                    "alt": None,
                    "width": 800,
                    "height": 441,
                    "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/abc.png?v=87654321",
                    "variant_ids": [],
                    "admin_graphql_api_id": "gid://shopify/ProductImage/123"
                },
                {
                    "id": 456,
                    "product_id": 123456789,
                    "position": 2,
                    "created_at": "2020-06-04T14:53:25-04:00",
                    "updated_at": "2020-06-10T17:58:28-04:00",
                    "alt": None,
                    "width": 2973,
                    "height": 4460,
                    "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/def.png?v=87654321",
                    "variant_ids": [],
                    "admin_graphql_api_id": "gid://shopify/ProductImage/456"
                },
                {
                    "id": 789,
                    "product_id": 123456789,
                    "position": 3,
                    "created_at": "2020-06-04T14:53:32-04:00",
                    "updated_at": "2020-06-10T17:58:28-04:00",
                    "alt": None,
                    "width": 2973,
                    "height": 4460,
                    "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/ghi.png?v=87654321",
                    "variant_ids": [],
                    "admin_graphql_api_id": "gid://shopify/ProductImage/789"
                },
                {
                    "id": 987,
                    "product_id": 123456789,
                    "position": 4,
                    "created_at": "2020-06-10T18:02:03-04:00",
                    "updated_at": "2020-06-10T18:07:46-04:00",
                    "alt": None,
                    "width": 2973,
                    "height": 4460,
                    "src": "https://cdn.shopify.com/s/files/1/2345/6789/0123/products/jkl.png?v=87654321",
                    "variant_ids": [],
                    "admin_graphql_api_id": "gid://shopify/ProductImage/987"
                }
            ],
            'image_updated': True
        }
    elif event_type == 'update_tags':
        return {
            'shop_domain': "example.myshopify.com",
            'product_id': 123456789,
            'existing_tags': ['Foo', 'Bar'],
            'new_tags': ['Tag1', 'Tag2'],
            'new_tags_count': 2
        }
    else:
        raise "Invalid event type."


if __name__ == '__main__':
    unittest.main()
