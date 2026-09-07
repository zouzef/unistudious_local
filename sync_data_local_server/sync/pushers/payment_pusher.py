import logging
import os
import sys
import json
import requests
from core.auth import get_token


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

# => API Sync function
def _send_update_Payment_Amount_api(settings, payload):
    try:
       token = get_token()
       headers = {"Authorization": f"Bearer {token}"}
       url = f"{settings.api_base_url}/slc/change-normal-payment-amount"
       response = requests.post(url, data=payload, headers=headers, timeout=10)

       if response.status_code == 200:
          logger.info("Payment Updated successfully")
          return True
       else:
          logger.error("Payment Update Failed")
          return False
    except Exception as e:
       print(e)
       logger.exception("Remote API error in update Payment Amount: %s", e)
       return False

def _send_update_Payment_status_api(settings, payload):
   try:
      token = get_token()
      headers = {"Authorization": f"Bearer {token}"}
      url = f"{settings.api_base_url}/slc/save-normal-payment-amount"

      response = requests.post(url, data=payload, headers=headers, timeout=10)

      if response.status_code == 200:
         logger.info("Payment saved successfully")
         return True
      else:
         logger.error("Payment Update Failed")
         return False

   except Exception as e:
      print(e)
      logger.exception("Remote API error in update Payment Status: %s", e)
      return False

def _send_cancel_payment_api(settings, payload):
   try:
      token = get_token()
      headers = {"Authorization": f"Bearer {token}"}
      url = f"{settings.api_base_url}/slc/update-status-cancel-normal-payment"
      response = requests.post(url, data=payload,headers=headers, timeout=10)
      print(response.status_code)
      if response.status_code == 200:
         logger.info("Payment saved successfully")
         return True
      else:
         logger.error("Payment Cancled Failed")
         return False
   except Exception as e:
      print(e)
      return False



def push_Amount_PaymentUpdate(db, settings, row):
    try:
       new_data   = json.loads(row.get('new_data', '{}'))
       session_id = new_data.get('session_id')
       user_id    = new_data.get('user_id')
       price      = new_data.get('price')

       UserIdProd = db.fetch_query("SELECT id_prod FROM user WHERE id = %s", (user_id,))
       SessionIdProd = db.fetch_query("SELECT id_prod FROM session WHERE id = %s", (session_id,))

       if not UserIdProd or not SessionIdProd:
          logger.error("Missing id_prod for user_id=%s or session_id=%s", user_id, session_id)
          return False

       user_id_prod = UserIdProd[0]['id_prod']
       session_id_prod = SessionIdProd[0]['id_prod']

       if user_id_prod is None or session_id_prod is None:
          logger.error("id_prod not yet synced for user_id=%s or session_id=%s", user_id, session_id)
          return False

       data = {
          "userId": user_id_prod,
          "sessionId": session_id_prod,
          "newAmount": price
       }
       success = _send_update_Payment_Amount_api(settings, data)
       return success

    except Exception as e:
       logger.exception("Error in push_UpdatePayment_Amount: %s", e)
       return False

def push_Payment_Save(db, settings, row):
   try:
      new_data         = json.loads(row.get('new_data', '{}'))
      session_id       = new_data.get('session_id')
      user_id          = new_data.get('user_id')
      payment_id       = new_data.get('payment_id')
      amount           = new_data.get('amount')
      price            = new_data.get('price')
      new_price        = new_data.get('new_price')
      change_price     = new_data.get('change_price')
      accept_payment   = new_data.get('accept_payment')
      amount_remaining = new_data.get('amount_remaining')
      description      = new_data.get('description') or ''

      UserIdProd = db.fetch_query("SELECT id_prod FROM user WHERE id = %s", (user_id,))
      SessionIdProd = db.fetch_query("SELECT id_prod FROM session WHERE id = %s", (session_id,))
      PaymentIdProd = db.fetch_query("SELECT id_prod FROM payment_session WHERE id = %s", (payment_id,))

      if not UserIdProd or not SessionIdProd or not PaymentIdProd:
         logger.error("Missing id_prod for user_id=%s, session_id=%s, payment_id=%s", user_id, session_id, payment_id)
         return False

      user_id_prod = UserIdProd[0]['id_prod']
      session_id_prod = SessionIdProd[0]['id_prod']
      payment_id_prod = PaymentIdProd[0]['id_prod']

      change_price_str = "yes" if change_price else "no"
      accept_payment_str = "yes" if accept_payment else "no"

      payload = {
         "paymentId":         payment_id_prod,
         "userId":            user_id_prod,
         "sessionId":         session_id_prod,
         "newAmount":         amount,
         "description":       description,
         "acceptPayment":     accept_payment_str,
         "changePrice":       change_price_str,
         "remainingPayment":  amount_remaining,
         "newPrice":          new_price
      }
      success = _send_update_Payment_status_api(settings, payload)
      return success

   except Exception as e:
      return False

def push_Cancel_Payment(db, settings, row):
   try:
      new_data = json.loads(row.get('new_data', '{}'))
      Payment_id_local = new_data.get('id')
      PaymentIdProd = db.fetch_query("SELECT id_prod FROM payment_session WHERE id = %s", (Payment_id_local,))
      payment_id_prod = PaymentIdProd[0]['id_prod']
      payload = {
         "id": payment_id_prod
      }
      success = _send_cancel_payment_api(settings, payload)
      return success


   except Exception as e:
      print(e)
      return False