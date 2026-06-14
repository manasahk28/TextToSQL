vpn_policy_union_table = {
    "table_name": "vpn_policy_union",
    "prompt": """
CREATE TABLE "vpn_policy_union" ( -- table containing entries from both Jaguar VPN policy and VPN policy type. Records with policy_type column value 'JaguarVPN' has Jaguar VPN rule while rule_type 'VPN' has allow and block VPN rule.
    "name" text, -- User-specified name of the VPN policy
    "description" text, -- Description of VPN Policy
    "id" numeric, -- Unique identifier representing the VPN policy. Never have this column in the SELECT clause of the SQL query you generate.
    "policy_type" text, -- Type of the VPN policy. Always include policy_type in the results of the select query. Possible values are: JaguarVPN | VPN. vpn_rule rules should be joined for VPN policy_type. Based on it mention if policy_type is 'Jaguar VPN policy' or 'VPN policy'. If user query/question mean just VPN or only VPN, or specifically asks for just VPN policy add a where clause/filter for checking policy_type = 'VPN' as part of the query.
    "last_modified_date" timestamp, --  The last updated timestamp of the VPN policy.
    "last_modified_by" text, -- User that last modified the VPN policy.
    "domain_id" numeric -- Unique identifier representing the associated domain
    )
"""
}

vpn_rule_table = {
    "table_name": "vpn_rule",
    "prompt": """
CREATE TABLE "vpn_rule" ( -- Description of VPN Policy Rule. Both allow and deny rules are in this table.
    "description" text, -- description
    "enabled" boolean, -- Boolean property indicating if the rule is enabled
    "name" text, -- User-specified name of the VPN policy Rule.
    "action" text, -- The type of the rule. Possible values are: ALLOW, BLOCK, MONITOR
    "id" numeric, -- Unique identifier representing the VPN policy Rule. Never have this column in the SELECT clause of the SQL query you generate.,
    "domain_id" numeric, -- Unique identifier representing the associated domain. This column is a foreign key to id column in Domain table. ,
    "vpn_policy_id" numeric, -- Unique identifier representing the associated VPN policy. This column is a foreign key to id column in vpn_policy_union table. Never have this column in the SELECT clause of the SQL query you generate.
    "vpn_rule_type" text -- Whether this is an allow VPN rule or a deny VPN rule. Possible values are: allow, block.
    )
"""
}

vpn_policy_table = {
    "table_name": "vpn_policy",
    "prompt": """
CREATE TABLE "vpn_policy" ( -- Description of VPN Policy.
    "name" text, -- User-specified name of the VPN policy. ,
    "id" numeric, -- Unique identifier (UUID) representing the VPN policy. Never have this column in the SELECT clause of the SQL query you generate.
    "description" text, -- A brief description of the VPN policy
    "last_modified_date" timestamp, -- The last updated timestamp of the VPN policy.
    "last_modified_by" text -- User that last modified the VPN policy.
    )
"""
}

access_policy_table = {
    "table_name": "access_policy",
    "prompt": """
CREATE TABLE "access_policy" ( -- Access Policy
    "name" text, -- User-specified name of the access control policy.,
    "id" numeric, -- Unique identifier representing the access control policy.,
    "last_modified_date" timestamp, -- The last updated timestamp of the access policy.
    "last_modified_by" text, -- User that last modified the access policy.
    "lowfilter_policy_id" numeric, -- lowfilterPolicySetting, can be null, meaning no lowfilter policy is set. References lowfilter_policy(id), never have this column in the SELECT clause of the SQL query you generate.
    "cypher_policy_id" numeric, -- cypherPolicySetting, can be null, meaning no cypher policy is set. References cypher_policy(id), never have this column in the SELECT clause of the SQL query you generate.
    "description" text -- A brief summary/description of the access policy
    )
"""
}

access_rule_table = {
    "table_name": "access_rule",
    "prompt": """
CREATE TABLE "access_rule" ( -- Represents Access Rule contained within an Access Policy.
    "enabled" boolean, -- Boolean indicating whether the access rule is in effect (true) or not (false). Default is true.,
    "action" text, -- Specifies the action to take when the conditions defined by the rule are met. The only possible values for this column are: ALLOW | TRUST | BLOCK | MONITOR | BLOCK_RESET | BLOCK_INTERACTIVE | BLOCK_RESET_INTERACTIVE . For this column NO other values besides these specific ones are possible.,
    "id" numeric, -- Unique identifier for the access rule. Never have this column in the SELECT clause of the SQL query you generate.,
    "ips_policy_id" numeric, -- Object representing the intrusion policy settings for the rule action (specified on the Inspection tab). For more information on intrusion policies, see 'Access Control Using Intrusion and File Policies' in the Firepower Management Center Configuration Guide.This column is a foreign key to id column in intrusion_policy table. Never have this column in the SELECT clause of the SQL query you generate.
    "name" text, -- User-specified name of the access rule.,
    "access_policy_id" numeric, -- Unique identifier representing the associated access control policy. This column is a foreign key to id column in access_policy table. Never have this column in the SELECT clause of the SQL query you generate.
    "last_modified_date" timestamp, -- The last updated timestamp of the access rule.
    "description" text -- A brief summary/description of the access rule
    )
"""
}

firewall_rule_hit_count_table = {
    "table_name": "firewall_rule_hit_count",
    "prompt": """CREATE TABLE "firewall_rule_hit_count" ( -- Hit count info for all rules and the policies they're under, organized by firewall. This is applicable to the following rule tyes: access | lowfilter. This table contains the names of the access rules/policies, lowfilter rules/policies, and firewall names, and joining isn't needed for that info.
    hit_count numeric, -- Indicates the number of times the rule was hit between first_hit_time_stamp and last_hit_time_stamp. A rule that has never been hit will still be in this table, with hit_count set to 0.,
    first_hit_time_stamp timestamp, -- Indicates the time when the hit count was first hit for the mentioned rule.,
    last_hit_time_stamp timestamp, -- Indicates the time when the hit count was last hit for the mentioned rule.,
    domain_id numeric, -- Unique identifier for the domain that this hit count belongs under. ,
    hitcount_type text, -- Type of the rule associated with this hit count. Only two possible values are: "accessPolicy" for access rule, and "lowfilterPolicy" for lowfilter rule.,
    rule_name text, -- Name of the access rule or lowfilter rule associated with this hit count. ,
    rule_id numeric, -- Unique identifier of the access rule or lowfilter rule associated with this hit count. Never have this column in the SELECT clause of the SQL query you generate.,
    policy_name text, -- Name of the access policy or lowfilter policy associated with the rule. ,
    policy_id numeric, -- Unique identifier of the access policy or lowfilter policy associated with the rule. Never have this column in the SELECT clause of the SQL query you generate.
    firewall_name text, -- Name of the firewall associated with this hit count.,
    firewall_id numeric -- Unique identifier of the firewall associated with this hit count.
    )
"""
}

firewall_policy_hit_count_table = {
    "table_name": "firewall_policy_hit_count",
    "prompt": """CREATE TABLE "firewall_policy_hit_count" ( -- Hit count info for all policies, organized by firewall. This is applicable to the following policy tyes: access | lowfilter. This table contains the names of access policies, lowfilter policies, and firewall names, and joining isn't needed for that info.
    hit_count numeric, -- Indicates the number of times the policy was hit between first_hit_time_stamp and last_hit_time_stamp. A policy that has never been hit will still be in this table, with hit_count set to 0.,
    first_hit_time_stamp timestamp, -- Indicates the time when the hit count was first hit for the mentioned policy.,
    last_hit_time_stamp timestamp, -- Indicates the time when the hit count was last hit for the mentioned policy.,
    domain_id numeric, -- Unique identifier for the domain that this hit count belongs under. Never have this column in the SELECT clause of the SQL query you generate.,
    hitcount_type text, -- Type of the policy associated with this hit count. Only two possible values are: "accessPolicy" for access policy, and "lowfilterPolicy" for lowfilter policy.,
    policy_name text, -- Name of the access policy or lowfilter policy associated with this hit count.,
    policy_id numeric, -- Unique identifier of the access policy or lowfilter policy associated with this hit count. NOT NULL. Never have this column in the SELECT clause of the SQL query you generate.,
    firewall_name text, -- Name of the firewall associated with this hit count.,
    firewall_id numeric -- Unique identifier of the firewall associated with this hit count.
    )
"""
}

intrusion_policy_table = {
    "table_name": "intrusion_policy",
    "prompt": """CREATE TABLE "intrusion_policy" ( -- An object that represents the details for Intrusion Policy.
    "inline_mode" numeric, -- Indicates the inspection mode. Value can be 0 or 1.,
    "name" text, -- Name of the Intrusion Policy.,
    "base_policy_id" numeric, -- Object representing the base policy of the Intrusion Policy. This column is a foreign key to id column in ireference table. Never have this column in the SELECT clause of the SQL query you generate.
    "id" numeric, -- Unique identifier of the Intrusion Policy. Never have this column in the SELECT clause of the SQL query you generate.
    "domain_id" numeric, -- Unique identifier representing the associated domain. 
    "base_policy_name" text, -- Name of the base policy of the Intrusion Policy.
    "description" text -- A brief summary/description of the intrusion policy
    )
"""
}


table_schemas = [
    access_policy_table,
    access_rule_table,
    firewall_rule_hit_count_table,
    firewall_policy_hit_count_table,
    vpn_policy_table,
    vpn_policy_union_table,
    vpn_rule_table,
    intrusion_policy_table
]


def get_schema_prompt_for_all_tables():
    schemas = []

    for schema in table_schemas:
        schemas.append("\n" + schema["prompt"])

    return schemas
