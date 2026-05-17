from flask import Blueprint, jsonify, request
from datetime import datetime
import sys
import os
import json


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required


account_level_bp = Blueprint('account_level',__name__, url_prefix='/scl')


@account_level_bp.route('/get_account_level/<int:account_id>',methods=['GET'])
def get_account_level(account_id):
	try:
		query = """
			SELECT 
				a.*,
				COALESCE(a.other_level, lc.name) AS level_name
			FROM account_level a
			LEFT JOIN level_config lc ON a.level_config_id = lc.id
			WHERE a.account_id = %s 
			  AND a.enabled = 1
			
		"""
		values = (account_id,)
		result = Database.execute_query(query,values,fetch=True)
		if result:
			return jsonify(result),200
		else:
			return jsonify({
				"Message":f"There is no level for this account"
			}),404

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500