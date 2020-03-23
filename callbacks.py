import mongodb as md
import iconactions as ica

def help_callback():
    return '''The following commands are at your disposal:
    /start,
    /hi,
    /commands ,
    /tip,
    /balance
        '''
def wallet_callback():
    return '''
    Wallet Information
    '''
def price_callback():
    value = str(ica.icx_usd())[:5]
    return '''
    USD/ICX = {}
    '''.format(value)
def apps_callback():
    return '''xyz
    Coming Soon!!!
    '''
    
def balance_callback(user_name):
    status, icx, irc2 = ica.get_balance_user(user_name)
    if status:
        return '''
        balances in your wallet:
        ICX: {}
        IRC2: {}
        '''.format(icx, irc2)
    
def address_callback(user_name):
    owner = md.find_one({"telegramUserId": user_name})
    return '''
    Address: {}
    Receive Address: {}
    '''.format(owner["address"], owner["address"])
    
def pk_callback(user_name):
    owner = md.find_one({"telegramUserId": user_name})
    return '''
    Private Key: {}
    '''.format(owner["privateKey"])