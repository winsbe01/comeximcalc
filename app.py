import pandas as pd
import numpy as np
import math
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result')
def result():
    band_size = request.args.get('band_size')
    cup_size = request.args.get('cup_size')
    store_name = request.args.get('store_name')
    res = calculate(int(band_size), cup_size, store_name)
    return render_template('result.html', band_size=band_size,
                        cup_size=cup_size, store_name=store_name,
                        res=res)


def calculate(band_size: int, cup_size: str, store_name: str) -> str:
    # Size options       
    uk_cup_letters = np.array(['A','B','C','D','DD','E','F','FF','G','GG','H','HH','J','JJ','K','KK','L','LL','M','MM']) # for LL+, order custom 
    pl_cup_letters = np.array(['A','B','C','D','E','F','G','H','HH','J','K','L','M','N','O','P','Q','R','S','T']) # for R+, order custom
    cup_numbers = np.array([i + 1 for i in range(len(uk_cup_letters))])
    uk_band_sizes = np.array([b*2 for b in range(12,26)]) # for < 28 or > 40, order custom
    pl_band_sizes = np.array([b*5 for b in range(10,24)]) # for < 60 or > 90, order custom

    # Conversion tables
    uk_cup_reference = pd.DataFrame(index=uk_cup_letters.T,data=cup_numbers.T,columns=['cup_number'])
    uk_cup_reference_rev = pd.DataFrame(index=cup_numbers.T,data=uk_cup_letters.T,columns=['cup_letter'])
    pl_cup_reference_rev = pd.DataFrame(index=cup_numbers.T,data=pl_cup_letters.T,columns=['pl_cup_letter'])
    pl_band_reference = pd.DataFrame(index=uk_band_sizes.T,data=pl_band_sizes.T,columns=['pl_band_sizes'])


    cup_number = uk_cup_reference.loc[cup_size].values[0]
    cup_cm = cup_number * 2.54  # centimeters
    new_cup_number = cup_cm / 2
    
    if new_cup_number - math.floor(new_cup_number) < 0.2:
        est_cup_number = [math.floor(new_cup_number)]
    elif new_cup_number - math.floor(new_cup_number) > 0.8:
        est_cup_number = [math.ceil(new_cup_number)]
    else:
        est_cup_number = [math.floor(new_cup_number),math.ceil(new_cup_number)]
    
    if store_name == 'Breakout Bras':
        est_cup_sizes = np.squeeze(uk_cup_reference_rev.loc[est_cup_number])
    elif store_name == 'Comexim':
        est_cup_sizes = np.squeeze(pl_cup_reference_rev.loc[est_cup_number])
        band_size = pl_band_reference.loc[band_size].values[0]
    else:
        return 'Please enter a valid store name in quotes (\"Breakout Bras\" or \"Comexim\")'
    
    if type(est_cup_sizes) == str:
        largest_cup = est_cup_sizes
        return 'Your estimated Comexim size when buying from {} is {}.'.format(store_name,str(band_size) + est_cup_sizes)
    else:
        largest_cup = est_cup_sizes.values[1]
        return 'Your estimated Comexim size when buying from {} is {}/{}.'.format(store_name,str(band_size) + est_cup_sizes.values[0],est_cup_sizes.values[1])
        
    custom_size = ((store_name == 'Breakout Bras' and ((band_size < 28 or band_size > 40) or (largest_cup in ['LL','M','MM']))) 
        or (store_name == 'Comexim' and ((band_size < 60 or band_size > 90) or (largest_cup in ['R','S','T']))))
    
    if custom_size:
        return 'You may need to contact Comexim to order a custom bra.'
    elif (store_name == 'Breakout Bras' and largest_cup == 'L'):
        return 'You may need to order directly from Comexim.'

