from typing import Dict, Any

class NTMappingService:
    """
    NT-Mapping Service (Osmium Standard)
    Acts as the 'Social Firewall' described by the NT_SPECIALIST.
    Translates complex, ambiguous neurotypical organizational structures (like LDAP/Active Directory)
    into flat, deterministic constants for Marc's ATLAS engine.
    """
    def __init__(self):
        # Maps complex AD roles to internal clear-cut ATLAS security clearance levels
        # Level 0 = Zero Trust (Guest)
        # Level 1 = Sensor / Edge Node
        # Level 5 = Admin / Architect (Marc / Dreadnought)
        
        self.ad_to_clearance_map = {
            "CN=Guest,OU=SmartHome,DC=unternehmen,DC=com": 0,
            "CN=Scanner,OU=IoT,DC=unternehmen,DC=com": 1,
            "CN=Marc,OU=Admin,DC=unternehmen,DC=com": 5
        }

    def translate_nt_identity(self, ldap_string: str) -> Dict[str, Any]:
        """
        Translates an external NT-actor string into an ATLAS-native identity block.
        """
        # Determine Clearance
        clearance = self.ad_to_clearance_map.get(ldap_string, 0) # Default to Zero Trust
        
        # Extract Actor Name (naive CN extraction for demonstration)
        actor_id = "UNKNOWN_ENTITY"
        if "CN=" in ldap_string:
            try:
                parts = ldap_string.split(",")
                for p in parts:
                    if p.startswith("CN="):
                        actor_id = p.split("=")[1].upper()
                        break
            except Exception:
                pass
        
        return {
            "original_nt_string": ldap_string,
            "actor_id_constant": f"ACTOR_{actor_id}",
            "system_clearance_level": clearance,
            "is_trusted": clearance >= 5
        }

if __name__ == "__main__":
    print("[ATLAS_CORE] Loading NT-Mapping Protocol...")
    mapper = NTMappingService()
    
    test_identities = [
        "CN=Guest,OU=SmartHome,DC=unternehmen,DC=com",
        "CN=Marc,OU=Admin,DC=unternehmen,DC=com",
        "CN=Unknown,OU=External,DC=unternehmen,DC=com"
    ]
    
    for identity in test_identities:
        mapped = mapper.translate_nt_identity(identity)
        print(f"\nIncoming NT Identity: {identity}")
        print(f"ATLAS Internal Mapping: {mapped}")
