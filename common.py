def print_status(test_name, success, message=""):
    status = "[SUCCESS]" if success else "[FAIL]"
    print(f"{test_name:<25} {status} {message}")
