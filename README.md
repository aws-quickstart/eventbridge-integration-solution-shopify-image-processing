# eventbridge-integration-solution-shopify-image-processing
## Amazon EventBridge Integration Solution for Shopify Image Processing

This Quick Start demonstrates an integration with AWS Step Function and AWS Lambda for Amazon EventBridge SaaS Partner Shopify. This solution enables your Amazon EventBridge event bus to trigger a rule that evaluates all events and invokes an AWS Step Functions state machine as a target for matched events. Once sent to Step Functions, Lambda functions are invoked that:

1. Extract the values like existing tags and image source URLs from the matched events
2. Detects the labels using Amazon Rekognition to be used as product tags
3. Updates the tags via the Shopify Admin API while maintaining existing product tags

You can use this as a starter project to extend this solution for any scenario that can use Step Functions and Lambda to orchestrate and run code.

![Quick Start architecture for EventBridge Integration Solution for Shopify Image Processing](https://github.com/aws-quickstart/eventbridge-integration-solution-shopify-image-processing/raw/master/images/arch-eventbridge-shopify-image-processing.png)


To post feedback, submit feature ideas, or report bugs, use the **Issues** section of [this GitHub repo](https://github.com/aws-quickstart/eventbridge-integration-solution-shopify-image-processing).
