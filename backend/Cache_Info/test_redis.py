import asyncio
import json
from redis_Create import Create
from redis_Read import Read
from redis_Update import Update
from redis_Delete import Delete

async def test_full_workflow():
    print("🔄 Test Full Redis Workflow...")
    

    
    # 2. READ
    print("\n2️⃣ READ phase...")
    read = Read()
    profile = await read.read_profile(7383551225813434369)
    email_exists = await read.read_by_email("fulltest@example.com")
    print(f"   ✅ Profile: {profile.get('name', 'N/A')} ({profile.get('email', 'N/A')})")
    print(f"   ✅ Email exists: {email_exists}")
    
    # 3. UPDATE
    print("\n3️⃣ UPDATE phase...")
    update = Update()
    update_result = await update.update_multiple_fields({
        "name": "Updated Full Test User",
        "email": "updated_fulltest@example.com",
        "role": "admin"
    }, "full_test_session")
    print(f"   ✅ Update result: {update_result}")
    
    # Verify update
    updated_profile = await read.read_profile("full_test_session")
    print(f"   ✅ Updated: {updated_profile.get('name', 'N/A')}")
    
    # 4. DELETE
    print("\n4️⃣ DELETE phase...")
    delete = Delete()
    logout_result = await delete.logout({
        "jti": "full_test_jti",
        "session_id": "full_test_session"
    })
    print(f"   ✅ Logout result: {logout_result}")
    
    # Verify deletion
    profile_after_delete = await read.read_profile("full_test_session")
    print(f"   ✅ After logout: {profile_after_delete}")
    
    print("\n🎉 Full workflow completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_full_workflow())