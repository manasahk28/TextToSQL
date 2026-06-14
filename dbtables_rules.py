
RULE_01 = {
    "tables": ["vpn_policy_union"],
    "prompt": """
When selecting VPN information from the 'vpn_policy_union' table, a filter of "VPN" should be applied to the 'policy_type' column
"""
}
RULE_O2 = {
    "tables": ["vpn_policy_union"],
    "prompt": """
To filter on *who modified a record* in table, use the 'last_modified_by' column if it exists and filter on the value of the given user name.
"""
}
RULE_O3 = {
    "tables": ["firewall_policy_hit_count", "firewall_rule_hit_count"],
    "prompt": """
Only use one of the two tables: firewall_policy_hit_count or firewall_rule_hit_count. 
These tables contain the same data, however, they are organized differently.`
"""
}
RULE_O4 = {
    "tables": ["firewall_policy_hit_count", "firewall_rule_hit_count"],
    "prompt": """
Do not add an order by clause to the query unless it is explicitly requested by the user.
"""
}
RULE_O5 = {
    "tables": ["access_policy", "intrusion_policy", "access_rule"],
    "prompt": """
access_policy needs to be joined first with access_rule to determine if an intrusion_policy is exists for the policy
"""
}
RULE_O6 = {
    "tables": ["firewall_rule_hit_count"],
    "prompt": """
do not filter on firewall_rule_hit_count.hit_count_type unless explicitly requested by the user
"""
}
all_rules = [RULE_01, RULE_O2, RULE_O3, RULE_O4, RULE_O5, RULE_O6]


def get_all_rules_for_tables():
    rules = []

    for rule in all_rules:
        rules.append("<rule>" + rule["prompt"] + "</rule>")

    return rules
