# Import python packages
import streamlit as st
import requests
import pandas as pd

from snowflake.snowpark.functions import col



# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothi :cup_with_straw:")
st.write(
    """Choose fruits you want in your custom Fruit Smoothie"""
)



name_on_order = st.text_input('name on smoothie')
st.write("The name on the smootie will be", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('search_on'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe
    ,max_selections=5
)


if ingredients_list: 
    ingredients_string = ''   

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + 'nutrition information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on )
        nutrition_data = smoothiefroot_response.json()
        sf_df = pd.DataFrame(nutrition_data)
        st.dataframe(data=sf_df, use_container_width=True)

    # Optional debug print
    # st.write(ingredients_string)

    my_insert_stmt = """insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string.strip() + """', '""" + name_on_order.strip() + """')"""


    # Optional debug print
    #st.write(my_insert_stmt)
    #st.stop()
    time_to_insert = st.button('submit order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


