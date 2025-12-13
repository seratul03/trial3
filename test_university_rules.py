"""
Test script for University Rules integration
Tests that the AI can properly access and respond to university rule queries
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/chat"
RULES_ENDPOINT = f"{BASE_URL}/api/university-rules"
SEARCH_ENDPOINT = f"{BASE_URL}/api/university-rules/search"

# Test queries covering different rule categories
TEST_QUERIES = [
    # Attendance & Examinations
    {
        "category": "Attendance",
        "query": "What is the minimum attendance required?",
        "expected_keywords": ["75%", "attendance", "exam"]
    },
    {
        "category": "Attendance",
        "query": "What attendance is needed for pharmacy students?",
        "expected_keywords": ["80%", "pharmaceutical"]
    },
    
    # Campus Rules
    {
        "category": "Campus Rules",
        "query": "What are the university timings?",
        "expected_keywords": ["8:00", "7:00", "pm"]
    },
    {
        "category": "Dress Code",
        "query": "What is the dress code policy?",
        "expected_keywords": ["uniform", "formal", "dress"]
    },
    {
        "category": "Mobile Phones",
        "query": "Can I use my mobile phone in class?",
        "expected_keywords": ["prohibited", "mobile", "academic"]
    },
    {
        "category": "ID Card",
        "query": "What happens if I lose my ID card?",
        "expected_keywords": ["100", "duplicate", "fine", "GD"]
    },
    
    # Library Rules
    {
        "category": "Library",
        "query": "How many books can I borrow from the library?",
        "expected_keywords": ["4", "books", "15 days"]
    },
    {
        "category": "Library Fines",
        "query": "What is the library overdue fine?",
        "expected_keywords": ["INR 5", "per day", "book"]
    },
    
    # Discipline
    {
        "category": "Banned Items",
        "query": "What items are banned on campus?",
        "expected_keywords": ["tobacco", "alcohol", "banned"]
    },
    {
        "category": "Penalties",
        "query": "What are the penalties for smoking on campus?",
        "expected_keywords": ["fine", "suspension", "banned"]
    },
    
    # Admissions
    {
        "category": "Placement",
        "query": "What is required for placement eligibility?",
        "expected_keywords": ["75%", "attendance", "placement"]
    },
    {
        "category": "Examination",
        "query": "What percentage is needed to pass an exam?",
        "expected_keywords": ["40%", "CIA", "TEE"]
    },
    
    # Canteen
    {
        "category": "Canteen",
        "query": "What are the canteen rules?",
        "expected_keywords": ["canteen", "queue", "clean"]
    }
]

def test_rules_api():
    """Test the university rules API endpoint"""
    print("=" * 80)
    print("TESTING UNIVERSITY RULES API")
    print("=" * 80)
    
    try:
        response = requests.get(RULES_ENDPOINT)
        data = response.json()
        
        if data.get('success'):
            print(f"✓ Rules API is working")
            print(f"  - Total Categories: {data['data']['total_categories']}")
            print(f"  - Total Rules: {data['data']['total_rules']}")
            print(f"\nCategories loaded:")
            for category, info in data['data']['categories'].items():
                print(f"  - {category}: {info['count']} rules")
            return True
        else:
            print(f"✗ Rules API returned error: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing rules API: {e}")
        return False

def test_rules_search():
    """Test the university rules search endpoint"""
    print("\n" + "=" * 80)
    print("TESTING UNIVERSITY RULES SEARCH")
    print("=" * 80)
    
    search_terms = ["attendance", "library", "mobile", "dress code", "fine"]
    
    for term in search_terms:
        try:
            response = requests.post(
                SEARCH_ENDPOINT,
                json={"query": term},
                headers={"Content-Type": "application/json"}
            )
            data = response.json()
            
            if data.get('success'):
                count = data['data']['count']
                print(f"✓ Search for '{term}': {count} rules found")
                if count > 0:
                    # Show first result
                    first = data['data']['rules'][0]
                    print(f"  Example: {first['title']}")
            else:
                print(f"✗ Search for '{term}' failed: {data.get('error')}")
                
        except Exception as e:
            print(f"✗ Error searching for '{term}': {e}")
    
    return True

def test_chat_responses():
    """Test chat responses for rule-related queries"""
    print("\n" + "=" * 80)
    print("TESTING CHAT RESPONSES FOR RULE QUERIES")
    print("=" * 80)
    
    results = {
        "total": len(TEST_QUERIES),
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    for i, test in enumerate(TEST_QUERIES, 1):
        print(f"\n[{i}/{len(TEST_QUERIES)}] Testing: {test['category']}")
        print(f"Query: {test['query']}")
        
        try:
            response = requests.post(
                CHAT_ENDPOINT,
                json={"query": test['query']},
                headers={"Content-Type": "application/json"}
            )
            data = response.json()
            answer = data.get('response', '').lower()
            
            # Check for expected keywords
            found_keywords = []
            missing_keywords = []
            
            for keyword in test['expected_keywords']:
                if keyword.lower() in answer:
                    found_keywords.append(keyword)
                else:
                    missing_keywords.append(keyword)
            
            # Determine pass/fail
            if len(found_keywords) >= len(test['expected_keywords']) * 0.5:  # At least 50% match
                results["passed"] += 1
                status = "✓ PASSED"
                color = "\033[92m"  # Green
            else:
                results["failed"] += 1
                status = "✗ FAILED"
                color = "\033[91m"  # Red
            
            print(f"{color}{status}\033[0m")
            print(f"Found keywords: {found_keywords}")
            if missing_keywords:
                print(f"Missing keywords: {missing_keywords}")
            print(f"Answer preview: {answer[:150]}...")
            
            results["details"].append({
                "category": test['category'],
                "query": test['query'],
                "status": "passed" if status == "✓ PASSED" else "failed",
                "found_keywords": found_keywords,
                "missing_keywords": missing_keywords,
                "answer": answer
            })
            
            # Brief delay between requests
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results["failed"] += 1
            results["details"].append({
                "category": test['category'],
                "query": test['query'],
                "status": "error",
                "error": str(e)
            })
    
    return results

def generate_report(results):
    """Generate a summary report"""
    print("\n" + "=" * 80)
    print("TEST SUMMARY REPORT")
    print("=" * 80)
    
    print(f"\nTotal Tests: {results['total']}")
    print(f"Passed: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    
    if results['failed'] > 0:
        print("\n\nFailed Tests:")
        for detail in results['details']:
            if detail['status'] == 'failed':
                print(f"\n  Category: {detail['category']}")
                print(f"  Query: {detail['query']}")
                print(f"  Missing: {detail.get('missing_keywords', [])}")
    
    # Save detailed results to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nDetailed results saved to: {filename}")

def main():
    """Main test runner"""
    print("\n" + "=" * 80)
    print("UNIVERSITY RULES INTEGRATION TEST SUITE")
    print("=" * 80)
    print("\nThis script tests the integration of university rules with the chatbot.")
    print("Make sure the Flask app is running on http://localhost:8000\n")
    
    input("Press Enter to start tests...")
    
    # Test 1: Rules API
    api_ok = test_rules_api()
    if not api_ok:
        print("\n⚠️  Warning: Rules API test failed. Chat tests may not work properly.")
        cont = input("\nContinue with remaining tests? (y/n): ")
        if cont.lower() != 'y':
            return
    
    # Test 2: Search API
    test_rules_search()
    
    # Test 3: Chat Responses
    results = test_chat_responses()
    
    # Generate Report
    generate_report(results)
    
    print("\n" + "=" * 80)
    print("TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    main()
