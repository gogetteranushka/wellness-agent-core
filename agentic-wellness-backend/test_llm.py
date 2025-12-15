from llm_client import preference_parser

print("=" * 60)
print("ENHANCED TEST: Rich preference extraction")
print("=" * 60)

result = preference_parser.parse(
    """I'm a college student, walk to classes daily, want to lose 5kg. 
    Vegetarian but eat eggs. I hate mushrooms and eggplant. 
    Love Punjabi and South Indian food. 
    Can only cook 10 mins in morning before class, 
    but have time for 30-min dinners. 
    Allergic to peanuts. Keep it simple, I'm not a great cook.
    Don't like very spicy food."""
)

print(f"Status: {result['status']}\n")
if result['status'] == 'success':
    import json
    print("EXTRACTED PREFERENCES:")
    print(json.dumps(result['structured'], indent=2))
    print(f"\nWarnings: {result['warnings']}")
else:
    print(f"Error: {result['message']}")
