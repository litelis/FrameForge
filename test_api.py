"""
Comprehensive API Test Script for AI Cinematic Video Editor
Tests all 4 phases and webhook functionality
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"
SESSION_ID = "test-session-comprehensive-001"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_phase1():
    """Test Phase 1: Prompt Refinement"""
    print_section("PHASE 1: PROMPT REFINEMENT")
    
    # Test refinement
    response = requests.post(f"{BASE_URL}/api/phase1/refine", json={
        "session_id": SESSION_ID,
        "original_prompt": "Make a nice video about my vacation"
    })
    
    if response.status_code != 200:
        print(f"❌ FAILED: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    print(f"✅ Refinement successful")
    print(f"   Issues detected: {len(data['result']['issues_detected'])}")
    print(f"   Improvements: {len(data['result']['improvements_made'])}")
    print(f"   Action required: {data['result']['user_action_required']}")
    
    # Test approval
    response = requests.post(f"{BASE_URL}/api/phase1/approve", json={
        "session_id": SESSION_ID,
        "approved": True
    })
    
    if response.status_code != 200:
        print(f"❌ Approval failed: {response.status_code}")
        return False
    
    print("✅ Prompt approved")
    return True

def test_phase2():
    """Test Phase 2: Intelligent Questioning"""
    print_section("PHASE 2: INTELLIGENT QUESTIONING")
    
    # Get questions
    response = requests.post(f"{BASE_URL}/api/phase2/questions", json={
        "session_id": SESSION_ID
    })
    
    if response.status_code != 200:
        print(f"❌ FAILED: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    questions = data['questions']
    print(f"✅ Generated {len(questions)} questions")
    
    # Submit answers for required questions
    required_questions = [q for q in questions if q.get('required', True)]
    print(f"   Required questions: {len(required_questions)}")
    
    for i, q in enumerate(required_questions[:2]):  # Answer first 2 required
        answer = q['options'][0] if q.get('options') else "Test answer"
        response = requests.post(f"{BASE_URL}/api/phase2/answer", json={
            "session_id": SESSION_ID,
            "question_id": q['id'],
            "answer": answer
        })
        
        if response.status_code == 200:
            print(f"   ✅ Answered: {q['id']}")
        else:
            print(f"   ❌ Failed to answer: {q['id']}")
    
    return True

def test_phase3():
    """Test Phase 3: Narrative Reasoning"""
    print_section("PHASE 3: NARRATIVE REASONING")
    
    response = requests.post(f"{BASE_URL}/api/phase3/analyze", json={
        "session_id": SESSION_ID
    })
    
    if response.status_code != 200:
        print(f"❌ FAILED: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    print("✅ Narrative analysis complete")
    print(f"   Arc: {data.get('narrative_summary', {}).get('arc', 'N/A')}")
    print(f"   Tone: {data.get('narrative_summary', {}).get('tone', 'N/A')}")
    return True

def test_phase4():
    """Test Phase 4: Scene Planning"""
    print_section("PHASE 4: SCENE PLANNING")
    
    response = requests.post(f"{BASE_URL}/api/phase4/plan", json={
        "session_id": SESSION_ID
    })
    
    if response.status_code != 200:
        print(f"❌ FAILED: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    scene_plan = data.get('scene_plan', {})
    
    print("✅ Scene planning complete")
    print(f"   Title: {scene_plan.get('title', 'N/A')}")
    print(f"   Theme: {scene_plan.get('theme', 'N/A')}")
    print(f"   Format: {scene_plan.get('format', 'N/A')}")
    print(f"   Scenes: {len(scene_plan.get('scenes', []))}")
    
    # Print first scene details
    scenes = scene_plan.get('scenes', [])
    if scenes:
        print(f"\n   First scene:")
        print(f"      Goal: {scenes[0].get('goal', 'N/A')[:50]}...")
        print(f"      Time: {scenes[0].get('start', 'N/A')} - {scenes[0].get('end', 'N/A')}")
    
    return True

def test_webhook_config():
    """Test Webhook Configuration"""
    print_section("WEBHOOK CONFIGURATION")
    
    response = requests.post(f"{BASE_URL}/api/webhook/config", json={
        "session_id": SESSION_ID,
        "webhook_config": {
            "webhook_url": "https://discord.com/api/webhooks/test/webhook",
            "enabled": True,
            "events": {
                "VIDEO_UPLOAD_STARTED": True,
                "PROMPT_REFINEMENT_STARTED": True,
                "SCENE_PLANNING_COMPLETED": True
            }
        }
    })
    
    if response.status_code != 200:
        print(f"❌ FAILED: {response.status_code}")
        print(response.text)
        return False
    
    print("✅ Webhook configuration saved")
    return True

def main():
    print("\n" + "="*60)
    print("  AI CINEMATIC VIDEO EDITOR - API TEST SUITE")
    print("="*60)
    print(f"Session ID: {SESSION_ID}")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Check if server is running
        response = requests.get(BASE_URL, timeout=5)
        print(f"\n✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Server not running at {BASE_URL}")
        print("Please start the server first: python app.py")
        sys.exit(1)
    
    # Run all tests
    results = []
    
    results.append(("Phase 1: Prompt Refinement", test_phase1()))
    results.append(("Phase 2: Intelligent Questioning", test_phase2()))
    results.append(("Phase 3: Narrative Reasoning", test_phase3()))
    results.append(("Phase 4: Scene Planning", test_phase4()))
    results.append(("Webhook Configuration", test_webhook_config()))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
