"""
Memory manager module for user preferences and context
"""
from cryptography.fernet import Fernet
from typing import Dict, Optional, Any
import json
from config import Config

class MemoryManager:
    """Manage user memory and preferences with encryption"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.cipher = None
        
        # Initialize encryption if key is provided
        if Config.FERNET_KEY:
            try:
                # Try to use the key directly (if it's already bytes)
                if isinstance(Config.FERNET_KEY, bytes):
                    self.cipher = Fernet(Config.FERNET_KEY)
                else:
                    # If it's a string, encode it
                    self.cipher = Fernet(Config.FERNET_KEY.encode())
            except Exception as e:
                print(f"Warning: Invalid Fernet key, generating new one for this session: {str(e)}")
                # Generate a new key for this session if the provided one is invalid
                key = Fernet.generate_key()
                self.cipher = Fernet(key)
                print(f"Temporary key for this session: {key.decode()}")
        else:
            # Generate a new key for this session
            key = Fernet.generate_key()
            self.cipher = Fernet(key)
            print(f"No Fernet key configured, using temporary key: {key.decode()}")
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a value"""
        if self.cipher:
            return self.cipher.encrypt(value.encode()).decode()
        return value
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a value"""
        if self.cipher:
            try:
                return self.cipher.decrypt(encrypted_value.encode()).decode()
            except Exception:
                return encrypted_value
        return encrypted_value
    
    def store_memory(self, user_id: int, key: str, value: Any) -> bool:
        """
        Store a memory item for a user
        
        Args:
            user_id: User identifier
            key: Memory key
            value: Value to store (will be JSON serialized)
            
        Returns:
            Success status
        """
        try:
            if self.db_session is None:
                return False
            
            from models import Memory
            
            # Serialize value
            value_str = json.dumps(value)
            
            # Encrypt value
            encrypted_value = self.encrypt_value(value_str)
            
            # Check if memory exists
            memory = self.db_session.query(Memory).filter_by(
                user_id=user_id,
                key=key
            ).first()
            
            if memory:
                memory.value = encrypted_value
            else:
                memory = Memory(
                    user_id=user_id,
                    key=key,
                    value=encrypted_value
                )
                self.db_session.add(memory)
            
            self.db_session.commit()
            return True
            
        except Exception as e:
            print(f"Error storing memory: {str(e)}")
            if self.db_session:
                self.db_session.rollback()
            return False
    
    def retrieve_memory(self, user_id: int, key: str) -> Optional[Any]:
        """
        Retrieve a memory item for a user
        
        Args:
            user_id: User identifier
            key: Memory key
            
        Returns:
            Stored value or None
        """
        try:
            if self.db_session is None:
                return None
            
            from models import Memory
            
            memory = self.db_session.query(Memory).filter_by(
                user_id=user_id,
                key=key
            ).first()
            
            if memory:
                # Decrypt value
                decrypted_value = self.decrypt_value(memory.value)
                
                # Deserialize value
                return json.loads(decrypted_value)
            
            return None
            
        except Exception as e:
            print(f"Error retrieving memory: {str(e)}")
            return None
    
    def get_all_memories(self, user_id: int) -> Dict[str, Any]:
        """
        Get all memories for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of all memories
        """
        try:
            if self.db_session is None:
                return {}
            
            from models import Memory
            
            memories = self.db_session.query(Memory).filter_by(
                user_id=user_id
            ).all()
            
            result = {}
            for memory in memories:
                try:
                    decrypted_value = self.decrypt_value(memory.value)
                    result[memory.key] = json.loads(decrypted_value)
                except Exception:
                    continue
            
            return result
            
        except Exception as e:
            print(f"Error retrieving memories: {str(e)}")
            return {}
    
    def delete_memory(self, user_id: int, key: str) -> bool:
        """
        Delete a memory item
        
        Args:
            user_id: User identifier
            key: Memory key
            
        Returns:
            Success status
        """
        try:
            if self.db_session is None:
                return False
            
            from models import Memory
            
            memory = self.db_session.query(Memory).filter_by(
                user_id=user_id,
                key=key
            ).first()
            
            if memory:
                self.db_session.delete(memory)
                self.db_session.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting memory: {str(e)}")
            if self.db_session:
                self.db_session.rollback()
            return False
    
    def build_user_context(self, user_id: int, role: str) -> str:
        """
        Build context string for user based on their memories and role
        
        Args:
            user_id: User identifier
            role: User role (lawyer, student, public)
            
        Returns:
            Context string
        """
        memories = self.get_all_memories(user_id)
        
        context = f"User Role: {role}\n"
        
        if memories:
            context += "\nUser Preferences:\n"
            for key, value in memories.items():
                context += f"- {key}: {value}\n"
        
        return context
