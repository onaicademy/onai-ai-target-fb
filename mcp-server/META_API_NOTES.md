# Meta Ads API Notes and Limitations

## Frequency Cap Visibility
The Meta Marketing API has some limitations regarding frequency cap visibility:

1. **Optimization Goal Dependency**: Frequency cap settings (`frequency_control_specs`) are only visible in API responses for ad sets where the optimization goal is set to REACH. For other optimization goals (like LINK_CLICKS, CONVERSIONS, etc.), the frequency caps will still work but won't be visible through the API.

2. **Verifying Frequency Caps**: Since frequency caps may not be directly visible, you can verify they're working by monitoring:
   - The frequency metric in ad insights
   - The ratio between reach and impressions over time
   - The actual frequency cap behavior in the Meta Ads Manager UI

## Other API Behaviors to Note

1. **Field Visibility**: Some fields may not appear in API responses even when explicitly requested. This doesn't necessarily mean the field isn't set - it may just not be visible through the API.

2. **Response Filtering**: The API may filter out empty or default values from responses to reduce payload size. If a field is missing from a response, it might mean:
   - The field is not set
   - The field has a default value
   - The field is not applicable for the current configuration

3. **Best Practices**:
   - Always verify important changes through both the API and Meta Ads Manager UI
   - Use insights and metrics to confirm behavioral changes when direct field access is limited
   - Consider the optimization goal when setting up features like frequency caps

## Updates and Changes
Meta frequently updates their API behavior. These notes will be updated as we discover new limitations or changes in the API's behavior. 