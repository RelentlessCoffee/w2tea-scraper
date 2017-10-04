from flask import Flask, url_for, render_template
import data


app = Flask(__name__)


@app.route('/')
def home_page():
    vendors = data.list_vendors()
    return render_template('home_page.html', vendors=vendors)


@app.route('/base')
def _base():
    vendors = data.list_vendors()
    return render_template('_base.html', vendors=vendors)


@app.route('/v')
def list_vendors():
    vendors = data.list_vendors()
    return render_template('list_vendors.html', vendors=vendors)


@app.route('/v/<vendor_id>')
def get_vendor(vendor_id):
    # TODO ADD VENDOR SUMMARIES
    return "some_vendor"


@app.route('/v/<vendor_id>/p/')
def list_products(vendor_id):
    products = data.list_products(vendor_id)
    vendors = data.list_vendors()
    return render_template('list_products.html', products=products, vendor_id=vendor_id, vendors=vendors)


@app.route('/v/<vendor_id>/p/<product_id>')
def get_product(vendor_id, product_id):
    samples = data.list_samples(vendor_id, product_id)
    product = data.get_product(vendor_id, product_id)
    vendors = data.list_vendors()
    return render_template('get_product.html', product=product, samples=samples, vendors=vendors)


with app.test_request_context():
    print(url_for('list_vendors'))
    print(url_for('get_vendor', vendor_id='w2t'))
    print(url_for('list_products', vendor_id='w2t'))
    print(url_for('get_product', vendor_id='w2t', product_id='my_cunt'))


if __name__ == "__main__":
    app.config.update(
        DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True
    )
    app.run()
