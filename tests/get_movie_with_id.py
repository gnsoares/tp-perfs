from concurrent.futures import wait
from requests_futures.sessions import FuturesSession
import time
import grpc

import movie_pb2
import movie_pb2_grpc

MOVIE_ID = '267eedb8-0f5d-42d5-8f43-72426b9fb3e6'


def run_rest_tests(n: int):
    print(f'Running {n} REST tests')
    with FuturesSession() as session:
        start = time.time()
        # start all requests
        futures = (session.get(f'http://movie_rest:5001/movies/{MOVIE_ID}')
                   for _ in range(n))
        # wait for all results
        list(map(lambda f: f.result(), futures))
        end = time.time()
    print(f'Total elapsed time for {n} tests: {end - start}s')
    return end - start


def run_grpc_tests(n: int):
    print(f'Running {n} gRPC tests')
    with grpc.insecure_channel('movie_grpc:3001') as channel:
        stub = movie_pb2_grpc.MovieStub(channel)
        movieid = movie_pb2.MovieID(id=MOVIE_ID)
        start = time.time()
        # start all requests
        futures = (stub.GetMovieByID.future(movieid) for _ in range(n))
        # wait for all results
        list(map(lambda f: f.result(), futures))
        end = time.time()
    print(f'Total elapsed time for {n} tests: {end - start}s')
    return end - start


def run_graphql_tests(n: int):
    print(f'Running {n} GraphQL tests')
    query = """query {{ movie_with_id(_id: "{movieid}") {{ ... on Movie {{
        id
        title
        rating
        director
    }} }} }}""".format(movieid=MOVIE_ID)
    with FuturesSession() as session:
        start = time.time()
        # start all requests
        futures = (session.post('http://movie_graphql:3301/graphql',
                                json={'query': query}) for _ in range(n))
        # wait for all results
        list(map(lambda f: f.result(), futures))
        end = time.time()
    print(f'Total elapsed time for {n} tests: {end - start}s')
    return end - start


def run_tests():
    n_tests = 100
    rest = run_rest_tests(n_tests)
    grpc = run_grpc_tests(n_tests)
    graphql = run_graphql_tests(n_tests)
    data = [rest, grpc, graphql]
    return data


if __name__ == '__main__':
    run_tests()
