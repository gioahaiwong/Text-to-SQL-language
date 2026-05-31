"""
 Copyright (c) 2020, salesforce.com, inc.
 All rights reserved.
 SPDX-License-Identifier: BSD-3-Clause
 For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

 Encode database content.
"""

import sqlite3
from rapidfuzz import fuzz

def get_database_matches(question, table_name, column_name, db_path, top_k_matches=2):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'SELECT DISTINCT "{column_name}" FROM "{table_name}" WHERE "{column_name}" IS NOT NULL')
        values = [str(row[0]) for row in cursor.fetchall()]
    except:
        values = []
    
    conn.close()
    
    if not values:
        return []
    
    # Simple fuzzy match to find relevant values from question
    matches = []
    question_lower = question.lower()
    
    for val in values:
        if val.lower() in question_lower:
            matches.append(val)
    
    # If no direct matches, use fuzzy
    if not matches:
        scored_values = []
        for val in values:
            score = fuzz.partial_ratio(val.lower(), question_lower)
            if score > 85:
                scored_values.append((val, score))
        
        scored_values.sort(key=lambda x: x[1], reverse=True)
        matches = [v[0] for v in scored_values[:top_k_matches]]
        
    return matches
