from flask import Blueprint, jsonify, request
import json
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database

formation_bp = Blueprint('formation', __name__, url_prefix='/scl')

@formation_bp.route('/get-formation-info/<int:account_id>',methods=['GET'])
def get_formation_info(account_id):
	try:
		query = """
			SELECT 
					f.id,
				   f.name,
				   f.description,
				   f.type_session,
				   f.number_day_duration,
				   f.number_session,
				   f.condition_of_passage
			 FROM formation f
			WHERE f.account_id = %s AND f.enabled = 1
		"""
		values = (account_id,)
		result = Database.execute_query(query,values)

		if result :
			return jsonify({
				"Data":result
			}),200
		else:
			return jsonify({
				"Message":"Error",
				"Data":[]
			}),404


	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from get_formation_info"
		}),500