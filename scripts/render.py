from datetime import datetime
import json
import os
import re

class InvalidAssetException(Exception):
    pass

class InvalidTemplateException(Exception):
    pass


def load_all(assets_dir):
    # First, find the summary JSON, which should be at the root of the
    # assets_dir.
    root_listdir = os.listdir(assets_dir)
    jsons = list(filter(lambda x: x.endswith('.json'), root_listdir))
    if len(jsons) != 1:
        raise InvalidAssetException(jsons)

    summary_json = os.path.join(assets_dir, jsons[0])
    with open(summary_json, 'r') as f:
        summary = json.load(f)

    # Load each category.
    categories = []
    for category_name in summary['categories']:
        category_dir = os.path.join(assets_dir, category_name)
        category_json = os.path.join(category_dir, '{}.json'.format(category_name))
        with open(category_json, 'r') as f:
            category = json.load(f)

        # Load each item.
        items = []
        for item in category['items']:
            if category['type'] == 'nested':
                item_json = os.path.join(
                category_dir,
                item,
                '{}.json'.format(item)
                )
            else:
                item_json = os.path.join(
                    category_dir,
                    '{}.json'.format(item)
                )
            with open(item_json, 'r') as f:
                items.append(json.load(f))
        category['items'] = items
        categories.append(category)

    summary['categories'] = categories
    return summary

def render_navigation(templates_dir, summary):
    navigation_dir = os.path.join(templates_dir, 'navigation')
    navigation_path = os.path.join(navigation_dir, 'navigation.html')
    navigation_item_path = os.path.join(navigation_dir, 'item.html')

    with open(navigation_path, 'r') as f:
        navigation_template = f.read()
    with open(navigation_item_path, 'r') as f:
        item_template = f.read()

    items = [item_template.format(**category) for category in summary['categories']]
    navigation = navigation_template.format(**{'items': '\n'.join(items)})

    return navigation

def render_general(templates_dir, summary, code):
    path = os.path.join(templates_dir, '{}.html'.format(code))
    with open(path, 'r') as f:
        template = f.read()
    return template.format(**summary)

def render_category_general(categories_dir, category, alt=False):
    type_dir = os.path.join(categories_dir, category['type'])
    category_path = os.path.join(type_dir, '{}.html'.format(category['type']))
    with open(category_path, 'r') as f:
        category_template = f.read()

    item_path = os.path.join(type_dir, 'item.html')
    with open(item_path, 'r') as f:
        item_template = f.read()

    items = []
    for item in category['items']:
        if item['description'] != None:
            body = '<p>{}</p>'.format(item['description'])
        elif item['bullet']:
            bullets = ['<li>{}</li>'.format(bullet) for bullet in item['bullet']]
            body = '<ul>{}</ul>'.format('\n'.join(bullets))
        else:
            body = ''

        if 'time' in item:
            time = item['time']
        else:
            time = '{} - {}'.format(item['time_start'], item['time_end'])

        if item['name_sub'] is None:
            item['name_sub'] = ''

        items.append(item_template.format(**{
            **item,
            'time': time,
            'body': body,
            'background-alt': 'background-alt' if not alt else 'background'
        }))

    category = category_template.format(**{
        **category,
        'items': '\n'.join(items),
        'background': 'background-alt' if alt else 'background'
    })
    return category

def render_category_list(categories_dir, category, alt=False):
    type_dir = os.path.join(categories_dir, category['type'])
    category_path = os.path.join(type_dir, '{}.html'.format(category['type']))
    with open(category_path, 'r') as f:
        category_template = f.read()

    items = ['<li>{}</li>'.format(item['name']) for item in category['items']]
    body = '<ul>{}</ul>'.format('\n'.join(items))

    category = category_template.format(**{
        **category,
        'body': body,
        'background': 'background-alt' if alt else ''
    })
    return category


def render_category_nested(categories_dir, category, alt=False):
    type_dir = os.path.join(categories_dir, 'list')
    category_path = os.path.join(type_dir, '{}.html'.format('list'))
    with open(category_path, 'r') as f:
        category_template = f.read()

    bodies = []
    for subcategory in category['items']:
        items = ['<li>{}</li>'.format(item['name']) for item in category['items']]
        bodies.append('<h3>{}</h3>\n<ul>{}</ul>'.format(subcategory['name'], '\n'.join(items)))

    category = category_template.format(**{
        **category,
        'body': '\n'.join(bodies),
        'background': 'background-alt' if alt else ''
    })
    return category

def render_categories(templates_dir, summary):
    categories_dir = os.path.join(templates_dir, 'categories')

    alt = True
    categories = []
    for category in summary['categories']:
        if category['type'] == 'nested':
            categories.append(render_category_nested(categories_dir, category, alt=alt))
        else:
            type_dir = os.path.join(categories_dir, category['type'])
            category_path = os.path.join(type_dir, '{}.html'.format(category['type']))
            with open(category_path, 'r') as f:
                category_template = f.read()

            if category['type'] == 'list':
                categories.append(render_category_list(categories_dir, category, alt=alt))
            else:
                categories.append(render_category_general(categories_dir, category, alt=alt))

        alt = not alt

    return '\n'.join(categories)

def render_links(templates_dir, summary):
    links_dir = os.path.join(templates_dir, 'links')
    links_path = os.path.join(links_dir, 'links.html')
    links_item_path = os.path.join(links_dir, 'item.html')

    with open(links_path, 'r') as f:
        links_template = f.read()
    with open(links_item_path, 'r') as f:
        item_template = f.read()

    items = [item_template.format(**{'name': name, 'link': link}) for name, link in summary['links'].items()]
    links = links_template.format(**{'items': '\n'.join(items)})

    return links

def render(assets_dir='assets', templates_dir='templates', out_dir='.'):
    summary = load_all(assets_dir)
    navigation = render_navigation(templates_dir, summary)
    lead = render_general(templates_dir, summary, 'lead')
    about = render_general(templates_dir, summary, 'about')
    categories = render_categories(templates_dir, summary)
    links = render_links(templates_dir, summary)

    # Render everything.
    index_path = os.path.join(templates_dir, 'index.html')
    with open(index_path, 'r') as f:
        index_template = f.read()
    index = index_template.format(**{
        **summary,
        'about': about,
        'categories': categories,
        'lead': lead,
        'links': links,
        'navigation': navigation,
    })

    with open(os.path.join(out_dir, 'index.html'), 'w') as f:
        f.write('<!--{}-->\n'.format(datetime.now()))
        f.write(index)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--assets_dir', type=str, default='assets')
    parser.add_argument('-t', '--templates_dir', type=str, default='templates')
    parser.add_argument('-o', '--out_dir', type=str, default='../')
    args = parser.parse_args()

    render(args.assets_dir, args.templates_dir, args.out_dir)
