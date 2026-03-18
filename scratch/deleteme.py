"""This script serves no purpose but for one off tests in case I forget to delete it.
If you find any content in this script either delete it and update the master or if useful:
1. Move it to appropriate module in src/fogbugz_py/
2. Write tests for it in tests/ folder.
3. Update documentation if necessary.

Useful scripts go in scripts/ folder at the root of the repo."""

# /// script
# dependencies = ["fogbugz-py", "tomli"]
# ///

import asyncio
import tomli
from pathlib import Path
from fogbugz_py import FogBugzClient


async def test_fogbugz_client():
    """Test FogBugz client with multiple queries using the library."""

    # Load config
    config_path = Path("config.toml")
    if not config_path.exists():
        print("❌ config.toml not found!")
        print("Please create config.toml with your FogBugz credentials.")
        return

    with open(config_path, "rb") as f:
        config = tomli.load(f)

    base_url = config["fogbugz"]["base_url"].rstrip("/")
    token = config["fogbugz"]["token"]

    print(f"🔗 Connecting to: {base_url}")
    print(
        f"🔑 Using token: {token[:10]}..." if len(token) > 10 else f"🔑 Token: {token}"
    )

    try:
        # Initialize the FogBugzClient using our library
        async with FogBugzClient(base_url=base_url, token=token) as client:

            # Test 1: Search for bugs assigned to S1
            print("\n" + "=" * 60)
            print("TEST 1: Search for bugs assigned to 'S1'")
            print("=" * 60)
            print(f"🔍 Query: assignedTo:S1")

            try:
                cases = await client.cases.search("assignedTo:S1")

                if cases:
                    print(f"✅ Success! Found {len(cases)} case(s):")
                    for case in cases:
                        print(f"\n  Case #{case.id}: {case.title}")
                        print(f"    Status: {case.status}")
                        print(f"    Assigned to: {case.assigned_to}")
                        print(f"    Project: {case.project}")
                else:
                    print("⚠️  No cases found assigned to S1")

            except Exception as e:
                print(f"❌ Error during search: {type(e).__name__}: {e}")

            # Test 2: Get specific case 25201
            print("\n" + "=" * 60)
            print("TEST 2: Get specific bug ID 25201")
            print("=" * 60)

            try:
                case = await client.cases.get(25201)

                print(f"✅ Success! Retrieved case 25201:")
                print(f"\n  Case #{case.id}: {case.title}")
                print(f"    Status: {case.status}")
                print(f"    Assigned to: {case.assigned_to}")
                print(f"    Project: {case.project}")
                print(f"    Priority: {case.priority}")
                print(f"    Area: {case.area}")
                print(f"    Category: {case.category}")

            except Exception as e:
                print(f"❌ Error retrieving case: {type(e).__name__}: {e}")

    except Exception as e:
        print(f"❌ Failed to initialize client: {type(e).__name__}: {e}")


if __name__ == "__main__":
    print("🚀 Testing FogBugz Client Library\n" + "=" * 60)
    asyncio.run(test_fogbugz_client())
    print("\n" + "=" * 60)
    print("✨ Test complete!")
