# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response

from product.models import Product, Category, Cart

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.template import RequestContext

import json

def index_view(request, templateName):
    # if 'openid' not in request.session:
    #    return HttpResponseRedirect('/code/?next=/')
    products = Product.objects.all().order_by('-sell')[:5]
    categorys = Category.objects.all()
    return render_to_response(templateName, {
        'products' : products,
        'categorys' : categorys,
        })

def product_view(request, c_id, templateName):
    # if 'openid' not in request.session:
    #     return HttpResponseRedirect('/code/?next=/' + c_id + '/product/')
    category = Category.objects.get(id = c_id)
    categoryName = category.name
    products = Product.objects.filter(category = category)
    categorys = Category.objects.all()
    return render_to_response(templateName, {
        'products' : products,
         'categorys' : categorys,
         'categoryName' : categoryName,
        })

def product_detail_view(request, p_id, templateName):
    # if 'openid' not in request.session:
    #     return HttpResponseRedirect('/code/?next=/product/' + p_id + '/')
    product = Product.objects.get(uid = p_id)
    categorys = Category.objects.all()
    return render_to_response(templateName, {
        'product' : product,
         'categorys' : categorys,
        })

def cart_view(request, templateName):
    # if 'openid' not in request.session:
    #     return HttpResponseRedirect('/code/?next=/cart/')
    cart = get_cart(request)
    print "cart_view+++", cart
    products = []
    for key, value in cart.items.items():
        item = Product.objects.get(uid = key)
        item.number = value
        products.append(item)
    categorys = Category.objects.all()
    return render_to_response(templateName, {
        'products' : products,
        'price' : cart.total,
        'categorys' : categorys,
        }, context_instance = RequestContext(request))

def get_cart(request):
    if 'cart' not in request.session:
        request.session['cart'] = Cart()
    return request.session['cart']

def clear_cart(request):
    success = False
    if request.method == 'POST':
        if 'cart' in request.session:
            request.session['cart'].clear()
        cart = get_cart(request)
        success = True
    return HttpResponse(json.dumps({
        'success' : success,
        }))

@csrf_exempt
def add_product(request):
    success = False
    if request.method == 'POST':
        productID = request.POST.get('productID', None)
        number = request.POST.get('number', None)
        del request.session['cart']
        cart = get_cart(request)
        print "add_product+++", cart
        if productID:
            product = Product.objects.get(uid = productID)
            cart.add(product,number)
            request.session['cart'] = cart
            print "yes+++",  request.session['cart']
            success = True
    return HttpResponse(json.dumps({
        'success' : success,
        }))

def reduce_product(request):
    success = False
    if request.method == 'POST':
        productID = request.POST.get('productID', None)
        cart = get_cart(request)
        if productID:
            product = Product.objects.get(uid = productID)
            cart.reduce(product)
            success = True
    return HttpResponse(json.dumps({
        'success' : success,
        }))

@csrf_exempt
def cancel_product(request):
    success = False
    if request.method == 'POST':
        productID = request.POST.get('productID', None)
        number = request.POST.get('number', None)
        cart = get_cart(request)
        if productID:
            product = Product.objects.get(uid = productID)
            cart.cancel(product,number)
            request.session['cart'] = cart
            success = True
    return HttpResponse(json.dumps({
        'success' : success,
        'total':request.session['cart'].total
        }))
