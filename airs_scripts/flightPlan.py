from config import FP_TOKEN
import flightplandb 
import asyncio
import json
import airs_scripts.geo as geo

async def main():
    await flightplandb.api.ping()
    result = await flightplandb.api.ping()
    print(result)

async def nats():
    key = FP_TOKEN
    await flightplandb.nav.nats(key)
    nats = await flightplandb.nav.nats()
    print(nats)

def hdg_Dist(lat1, lon1, lat2, lon2):
    track_mag, track_true, dist = geo.heading_to_destination(lat1, lon1, lat2, lon2)
    return track_mag, track_true, dist

def update_node_dict(node_list):
    node_data = []
    for i, node in enumerate(node_list[:-1]):
        lat1, lon1 = node['lat'], node['lon']
        lat2, lon2 = node_list[i+1]['lat'], node_list[i+1]['lon']
        track_mag, track_true, dist = hdg_Dist(lat1, lon1, lat2, lon2)
        node_data.append({'ident': node['ident'],
                          'type': node['type'],
                          'lat': node['lat'],
                          'lon': node['lon'],
                          'alt': node['alt'],
                          'via': node['via'],
                          'track_mag': track_mag,
                          'track_true': track_true,
                          'dist': dist})
    node_data.append(node_list[-1])
    return node_data


async def flightPlan(dep, dest):
    key = FP_TOKEN
    gen_query = flightplandb.datatypes.GenerateQuery(fromICAO=dep, toICAO=dest)
    plan = await flightplandb.plan.generate(gen_query=gen_query, include_route=True, key=key)
    
    plan_id = json.dumps(plan.id)
    
    plan_json = await flightplandb.plan.fetch(plan_id, return_format="json")
    try:
        plan_dict = json.loads(plan_json)
        route = plan_dict['route']['nodes']
        node_list = []
        for node in route:
            node_dict = {}
            node_dict['ident'] = node['ident']
            node_dict['type'] = node['type']
            node_dict['lat'] = node['lat']
            node_dict['lon'] = node['lon']
            node_dict['alt'] = node['alt']
            node_dict['via'] = node['via']
            node_list.append(node_dict)

        node_data = update_node_dict(node_list)

    except:
        node_data

    return node_data





#asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#asyncio.run(main())

