from flask import Blueprint, request, jsonify
import os
import sys
import json
from config import Config
from core.database import Database
from core.middleware import token_required
from datetime import datetime, date


season_bp = Blueprint('season', __name__, url_prefix='/scl')

@season_bp.route('/create-season', methods=['POST'])
def create_season():
	try:
		data = request.get_json()
		FormationId = data.get('formation_id')
		Account_id = data.get('account_id')
		Title= data.get('title')
		Description = data.get('description')
		TypeDuration = data.get('type_duration')
		NumberDuration = data.get('number_duration')

		query ="""
			INSERT INTO season
			(formation_id,account_id,title,description,status,type_duration,number_duration,enabled,created_at,timestamp)
			VALUES(%s,%s,%s,%s,1,%s,%s,1,NOW(),NOW())
		"""
		values=(FormationId,Account_id,Title,Description,TypeDuration,NumberDuration)
		response = Database.execute_query(query, values,fetch=False)
		if response:
			new_record = Database.execute_query(
				"SELECT * FROM season WHERE id = %s",
				(response,),
				fetch=True
			)
			log_audit(
				action_type="INSERT",
				old_data=None,
				new_data=new_record[0] if new_record else data
			)
			return jsonify({"Message":"Season created with success"}),200
		else:
			return jsonify({"Message": "Error in creating season"}), 400

	except Excepton as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		}),500