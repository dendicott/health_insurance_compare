import numpy as np
import pandas as pd
import plotly.express as px

def spend_calculation(dframe,plan,spend,tax_rate):
    cost_adj = []
    for spent in spend:
        if spent <= dframe['Deductible'][plan]:
            spent_calc = spent - dframe['Employer Contribution'][plan] + dframe['Bi-weekly Dues'][plan] * 26.0 - dframe['Tax Deduction'][plan] * tax_rate
            cost_adj.append(spent_calc)
        elif spent > dframe['Deductible'][plan] and dframe['Deductible'][plan] + (spent - dframe['Deductible'][plan]) * dframe['Coinsurance'][plan] <= dframe['OOP Max'][plan]:
            spent_calc = dframe['Deductible'][plan] + ((spent - dframe['Deductible'][plan]) * dframe['Coinsurance'][plan]) - dframe['Employer Contribution'][plan] + dframe['Bi-weekly Dues'][plan] * 26 - dframe['Tax Deduction'][plan] * tax_rate
            cost_adj.append(spent_calc)
        else:
            spent_calc = dframe['OOP Max'][plan] - dframe['Employer Contribution'][plan] + dframe['Bi-weekly Dues'][plan] * 26 - dframe['Tax Deduction'][plan] * tax_rate
            cost_adj.append(spent_calc)
    return cost_adj

def employee_cost(dependents, tax_rate):
    
    tax_rate = tax_rate / 100.00
    spend = np.linspace(0.0,50000.0,100)
    
    data = {'Plans':['HDHP','EPO','PPO'],'Deductible':[0.0,0.0,0.0],
        'OOP Max':[0.0,0.0,0.0],'Employer Contribution':[0.0,0.0,0.0],
        'Tax Deduction':[0.0,0.0,0.0],'Coinsurance':[0.0,0.0,0.0],
        'Bi-weekly Dues':[0.0,0.0,0.0]}
    
    bi_weekly_dues = {'EPO-EO':0.0,'EPO-ES':95.00,'EPO-EC':70.00,'EPO-EF':150.00,
        'PPO-EO':35.00,'PPO-ES':110.00,'PPO-EC':80.00,'PPO-EF':180.00, 
        'HDHP-EO':25.00,'HDHP-ES':100.00,'HDHP-EC':75.00,'HDHP-EF':165.00}
    
    oop_max = {'EPO-EO':3500.00,'EPO-ES':7000.00,'EPO-EC':7000.00,'EPO-EF':7000.00,
        'PPO-EO':7000.00,'PPO-ES':7000.00,'PPO-EC':7000.00,'PPO-EF':7000.00, 
        'HDHP-EO':4500.00,'HDHP-ES':9000.00,'HDHP-EC':9000.00,'HDHP-EF':9000.00}

    deductible = {'EPO-EO':500.0,'EPO-ES':1000.0,'EPO-EC':1000.0,'EPO-EF':1000.0,
        'PPO-EO':500.00,'PPO-ES':1000.0,'PPO-EC':1000.0,'PPO-EF':1000.0, 
        'HDHP-EO':1500.00,'HDHP-ES':3000.00,'HDHP-EC':3000.00,'HDHP-EF':3000.00}    

    employer_contribution = {'EPO-EO':0.0,'EPO-ES':0.0,'EPO-EC':0.0,'EPO-EF':0.0,
        'PPO-EO':0.0,'PPO-ES':0.0,'PPO-EC':0.0,'PPO-EF':0.0, 
        'HDHP-EO':500.00,'HDHP-ES':1000.00,'HDHP-EC':1000.00,'HDHP-EF':1000.00} 

    tax_deduction = {'EPO-EO':0.0,'EPO-ES':0.0,'EPO-EC':0.0,'EPO-EF':0.0,
        'PPO-EO':0.0,'PPO-ES':0.0,'PPO-EC':0.0,'PPO-EF':0.0, 
        'HDHP-EO':3550.00,'HDHP-ES':7100.00,'HDHP-EC':7100.00,'HDHP-EF':7100.00} 

    coinsurance = {'EPO-EO':0.15,'EPO-ES':0.15,'EPO-EC':0.15,'EPO-EF':0.15,
        'PPO-EO':0.20,'PPO-ES':0.20,'PPO-EC':0.20,'PPO-EF':0.20, 
        'HDHP-EO':0.20,'HDHP-ES':0.20,'HDHP-EC':0.20,'HDHP-EF':0.20} 

    dframe = pd.DataFrame(data)
    dframe = dframe.set_index('Plans')

    for plan in data['Plans']:
        string_construct = plan + '-' + dependents
        
        dframe['Bi-weekly Dues'][plan]        = bi_weekly_dues[string_construct]
        dframe['OOP Max'][plan]               = oop_max[string_construct]
        dframe['Deductible'][plan]            = deductible[string_construct]      
        dframe['Employer Contribution'][plan] = employer_contribution[string_construct]
        dframe['Tax Deduction'][plan]         = tax_deduction[string_construct]
        dframe['Coinsurance'][plan]           = coinsurance[string_construct]
    
   
    hdhp_cost_adj = spend_calculation(dframe,'HDHP',spend,tax_rate)
    epo_cost_adj = spend_calculation(dframe,'EPO',spend,tax_rate)
    ppo_cost_adj = spend_calculation(dframe,'PPO',spend,tax_rate)
    
    return dframe, spend, dependents, hdhp_cost_adj, epo_cost_adj, ppo_cost_adj

print("""
////////////////////////////// NOTE ////////////////////////////////////
This program makes the following assumptions:
Medical spend is the total annual cost of health care.
HDHP implies a fully funded HSA
All spending is in-network.
All spending beyond deductible up to OOP Max is covered by coinsurance.
////////////////////////////////////////////////////////////////////////
""")

dependent_input = input("""
What type of plan are you looking for?
Possible arguments include:
EO = Employee Only
ES = Employee + Spouse
EC = Employee + Children
EF = Employee + Family
""")

dependent_input = dependent_input.upper()

tax_input = input("""
What tax bracket would you like to simulate?
Input should be as follows: XX (representing XX% federal tax bracket)
"""
)

tax_input = float(tax_input)

health_data = employee_cost(dependent_input,tax_input)

dependents = health_data[2]

cost_df = pd.DataFrame(index=health_data[1])
cost_df['HDHP'] = health_data[3] 
cost_df['EPO'] = health_data[4]
cost_df['PPO'] = health_data[5]

fig = px.line(cost_df,x = cost_df.index, y=[cost_df['HDHP'], cost_df['EPO'], cost_df['PPO']],template="plotly_dark")
fig.update_layout(legend_title_text='Plans',
                    xaxis_title='Annual Medical Spend ($)',
                    yaxis_title='Employee Adjusted Cost ($)',
                    title={'text': 'Health Plan Adjusted Cost'})
fig.add_annotation(text="Negative adjusted cost is cash in your pocket",
                    xref="paper", yref="paper",
                    x=0.01, y=1.0, showarrow=False)
fig.show()

