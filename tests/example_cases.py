# A subset of the test cases for this approach

example_case_00 = {
    # "note": "the sql generated for this user query was incorrect - missing filter on 'VPN'",
    "user_query": "List my VPN Policies",
    "sql": "SELECT DISTINCT vpn_policy_union.name, vpn_policy_union.policy_type FROM vpn_policy_union",
}

example_case_01 = {
    # "note": "the sql generated for this user query was incorrect - missing filter on 'admin'",
    "user_query": "Which of my VPN policies have been modified by 'admin'?",
    "sql": """SELECT DISTINCT vpn_policy_union.name, vpn_policy_union.policy_type, vpn_policy_union.last_modified_by 
    FROM vpn_policy_union
    WHERE vpn_policy_union.last_modified_by IS NOT NULL""",
}

example_case_02 = {
    # "note": "the sql generated for this user query was incorrect - column access_policy.ips_policy_id does not exist",
    "user_query": "Which ACP policies have an assigned intrusion policy?",
    "sql": """
SELECT DISTINCT access_policy.name
FROM access_policy
WHERE access_policy.ips_policy_id IS NOT NULL""",
}

example_case_03 = {
    # "note": "the sql generated for this user query was incorrect - it is overly restrictive with hitcount_type
    #         "query should also be much simpler since all the info necessary is in the firewall_rule_hit_count table",
    "user_query": "what are my never hit rules? Include the policy name in the result",
    "sql": """SELECT DISTINCT access_policy.name AS policy_name, access_rule.name AS rule_name 
FROM access_policy 
JOIN access_rule ON access_policy.id = access_rule.access_policy_id
LEFT JOIN firewall_rule_hit_count ON access_rule.id = firewall_rule_hit_count.rule_id AND firewall_rule_hit_count.hitcount_type = 'AccessMode'
WHERE firewall_rule_hit_count.hit_count IS NULL OR firewall_rule_hit_count.hit_count = 0""",
}

example_case_04 = {
    # "note": "the sql generated for this user query was incorrect - it creates an UNION between policy and rules tables when the question is clearly only about policies",
    "user_query": "Which policies have hit counts greater than 0?",
    "sql": """SELECT DISTINCT p.policy_name, p.hitcount_type, p.hit_count 
FROM (
    SELECT policy_name, hitcount_type, hit_count
    FROM firewall_policy_hit_count
    WHERE hit_count > 0
    UNION
    SELECT policy_name, hitcount_type, hit_count 
    FROM firewall_rule_hit_count
    WHERE hit_count > 0
) p""",
}

example_case_05 = {
    # "note": "This test should produce and equivalent answer",
    "user_query": "List my VPN policies that are a VPN policy type",
    "sql": """SELECT DISTINCT vpn_policy_union.name, vpn_policy_union.policy_type
FROM vpn_policy_union
WHERE vpn_policy_union.policy_type = 'VPN'
""",
}

example_case_06 = {
    # "note": "This test should produce and equivalent answer",
    "user_query": "Is there an intrusion policy named Baseline Detection?",
    "sql": """SELECT name, summary FROM intrusion_policy 
WHERE name LIKE 'Baseline Detection'
""",
}



def get_example_case(index: int):
    # a list of example user requests (aka queries)
    example_cases = [
        example_case_00,
        example_case_01,
        example_case_02,
        example_case_03,
        example_case_04,
        example_case_05,
        example_case_06
    ]

    # Check if the index is in bounds,  if not, return an empty string
    if index < 0 or index >= len(example_cases):
        print(f"Test input index: {index} is out of bounds")
        return ""
    # return an example case based on an index
    test_case = example_cases[index]
    return test_case