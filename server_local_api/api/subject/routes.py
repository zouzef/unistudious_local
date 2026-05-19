from flask import Blueprint, jsonify, request  # ← only one import line
import sys
import os
import json
from datetime import datetime, timedelta
import bcrypt
import mysql.connector

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from core.database import Database
from core.middleware import token_required


subject_bp = Blueprint('subjects', __name__, url_prefix='/scl')


# ========================================
# ENDPOINT 1: Get all sub_subject
# ========================================
@subject_bp.route('/get_sub_subjects', methods=['GET'])  # ← fixed
def get_subjects():
    try:
        query = """
            SELECT 
                a.subject_config_id,
                CASE 
                    WHEN a.other_subject IS NOT NULL THEN a.other_subject
                    ELSE sc.name
                END AS subject_identifier
            FROM account_subject a
            LEFT JOIN subject_config sc ON sc.id = a.subject_config_id
        """
        result = Database.execute_query(query,fetch=True)
        return jsonify({
            "Message":"Success",
            "data":result
        }),200
    except Exception as e:
        print(f"Error coming from the get_subject: {e}")
        return jsonify({
            "Message": f"Error: {e} coming from the server"
        }), 500

@subject_bp.route('/get_subject_config',methods=['GET'])
def get_subject_config():
    try:
        query = """
            SELECT *
            FROM subject_config
            WHERE enabled = 1
        """
        result = Database.execute_query(query,fetch=True)
        if result:
            return jsonify(result),200
        else:
            return jsonify({
                "Message":"There is no subjects for this account"
            }),404

    except Exception as e:
        return jsonify({
            "Message":f"Error: {e} coming from server"
        }),500

@subject_bp.route('/get_account_subject/<int:account_id>',methods=['GET'])
def get_account_subject(account_id):
    try:
        query = """
            SELECT DISTINCT
                a.id,
                a.account_id,
                a.subject_config_id,
                a.description,
                a.enabled,
                a.status,
                CASE 
                    WHEN a.other_subject IS NOT NULL THEN a.other_subject
                    ELSE s.name 
                END AS section_name
            FROM account_subject a
            LEFT JOIN subject_config s ON s.id = a.subject_config_id
            WHERE a.account_id = %s AND a.enabled = 1 AND s.enabled = 1
        """
        values= (account_id,)
        result = Database.execute_query(query,values,fetch=True)
        if result:
            return jsonify(result),200
        else:
            return jsonify({
                "Message":"There is no account_subject for this id"
            }),404
    except Exception as e:
        return jsonify({
            "Message":f"Error: {e} coming from server "
        })

@subject_bp.route('/delete_account_subject/<account_subject_id>',methods=['POST'])
def delete_account_subject(account_subject_id):
    try:
        query = """
            UPDATE account_subject
            SET enabled = 0
            WHERE id =%s
            
        """
        values =(account_subject_id,)
        result = Database.execute_query(query,values,fetch=False)
        if result:
            return jsonify({
                "Message":f"Subject_config deleted with success"
            }),200
        else:
            return jsonify({
                "Message":f"Error in deleting subject_config"
            }),400
    except Exception as e:
        return jsonify({
            "Message":f"Error: {e} coming from server"
        }),500

@subject_bp.route('/view_account_subject/<int:account_subject_id>',methods=['GET'])
def view_account_subject(account_subject_id):
    try:
        query = """
            SELECT 
                a.id,
                a.account_id,
                a.subject_config_id,
                a.description,
                a.enabled,
                a.status,
                CASE 
                    WHEN a.other_subject IS NOT NULL THEN a.other_subject
                    ELSE s.name 
                END AS section_name
            FROM account_subject a
            LEFT JOIN subject_config s ON s.id = a.subject_config_id
            WHERE a.id = %s AND a.enabled = 1 AND s.enabled = 1
        
        """
        result = Database.execute_query(query,(account_subject_id,),fetch=True)
        if result:
            return jsonify(result),200
        else:
            return jsonify({
                "Message":"There is no Data for this id"
            }),404
    except Exception as e:
        return jsonify({
            "Message":f"Error: {e} coming from backend"
        }),500

@subject_bp.route('/create_account_subject/<int:account_id>',methods=['POST'])
def create_account_subject(account_id):
    try:
        data = request.get_json()
        subject_id = data.get('subjectId')
        other_subject = data.get('other_subject') or None
        description = data.get('description') or None
        if not (subject_id):
            return jsonify({
                "Message":"Missing subject_id"
            }),404

        query = """
            INSERT INTO account_subject(account_id,subject_config_id,status,description,other_subject,enabled,created_at,timestamp,slc_use)
            VALUES(%s,%s,1,%s,%s,1,NOW(),NOW(),1)        
        """
        values=(account_id,subject_id,description,other_subject)
        result = Database.execute_query(query,values,fetch=False)
        if result:
            return jsonify({
                "Message":"subject_config created with success"
            }),200
        else:
            return jsonify({
                "Message":"Error in creating subject_config"
            }),400

    except Exception as e:
        return jsonify({
            "Message":f"Error: {e} coming from server"
        }),500