

def product_access_unit_cost(product_unit,product_quantity):
    if product_unit == 'Kg':
        cost = product_quantity/100
    else:
        cost = (product_quantity*1000)/100
    return cost


#print(product_access_unit_cost('T',25))