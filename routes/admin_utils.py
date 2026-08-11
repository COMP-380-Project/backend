"""
Admin/Manager Permission Helper

* **Date:** 8/10/26
* **Programmer:** Mark Antonov

Shared helper used by manager-only routes to verify the requesting
customer has manager-level access before allowing an action.
"""
from models.customer import Customer


def require_manager(customer_id):
    """
    Check whether a given customer_id belongs to a manager.

    Args:
        customer_id (int): ID of the customer making the request

    Returns:
        tuple: (Customer or None, error_response or None)
            If valid manager: (customer, None)
            If not: (None, (json_error, status_code))
    """
    if not customer_id:
        return None, ({'error': 'Missing customer_id'}, 400)

    customer = Customer.query.get(customer_id)

    if not customer:
        return None, ({'error': 'Customer not found'}, 404)

    if customer.role != 'manager':
        return None, ({'error': 'Manager access required'}, 403)

    return customer, None