from data import engine, Product
import pendulum
import matplotlib.dates
import matplotlib.pyplot


def create_query(name):
    return engine.query(
        Product,
        key=Product.name == name
    )


def query_list(product_name):
    query = create_query(product_name)
    product_data_list = list(query)
    return product_data_list

# foo = []
# for result in results:
#     foo.append(result.quantity)


def filtered_between(product_data_list, start_date, end_date):
    results = []
    start = pendulum.parse(start_date)
    end = pendulum.parse(end_date)
    for result in product_data_list:
        # if result.date >= start and result.date <= end:
        if start <= result.date <= end:
                results.append(result)
    return results


def extract_dates(results):
    dates = [r.date for r in results if r.quantity is not None]
    return dates


def quantities(results):
    quantities = [r.quantity for r in results if r.quantity is not None]
    return quantities


def largest_smallest_dates(results):
    results = [r for r in results if r.quantity is not None]
    results = sorted(results, key=lambda result: result.quantity)
    # return (results[0].date, results[0].quantity), (results[-1].date, results[-1].quantity)
    result = {
        "smallest": results[0].date,
        "largest": results[-1].date
    }
    return result


def percent_of_none(results):
    all_quantities = len([r.quantity for r in results])
    quantities_list = len(quantities(results))
    pon = 100 - (100 * (quantities_list / all_quantities))
    return pon
    # product example "w2t.duck-shit-oolong."


def average_quantity(results):
    quantities_list = quantities(results)
    foo = sum(quantities_list)
    bar = len(quantities_list)
    average = foo/bar
    return average


def smallest_largest(results):
    quantities_list = quantities(results)
    sorted_list = sorted(quantities_list)
    return sorted_list[0], sorted_list[-1]


def get_status():
    product_name = "w2t.duck-shit-oolong."
    start_date = '2017-03-01'
    end_date = '2017-10-01'
    results = query_list(product_name)
    results = filtered_between(results, start_date, end_date)
    status = {
        "quantity.smallest": smallest_largest(results)[0],
        "quantity.largest": smallest_largest(results)[1],
        "date.smallest": largest_smallest_dates(results)["smallest"],
        "date.largest": largest_smallest_dates(results)["largest"],
        "average": average_quantity(results),
        "percent none": percent_of_none(results)
    }
    return status


get_status()


# def plot():
#     results = product()
#     list_quantities = quantities(results)
#     dates = matplotlib.dates.date2num(extact_dates(results))
#     matplotlib.pyplot.plot_date(dates, list_quantities)
#     print(results)
#     print(results[0].url)
#     matplotlib.pyplot.show()
#
# plot()
