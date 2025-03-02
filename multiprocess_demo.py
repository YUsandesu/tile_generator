import multiprocessing
import time

def process_chunk(chunk):
    """Calculate the sum of squares for a chunk of data."""
    return sum(x * x for x in chunk)

if __name__ == '__main__':

    #尽量用NP模块,因为优化更好

    num_processes = round(multiprocessing.cpu_count() * 0.9) # Use all available CPUs
    print(num_processes)
    #尽量别用全,全部使用会导致其他软件延迟.

    data = list(range(num_processes * 30000000))

    # Split data into chunks for multiprocessing
    chunk_size = len(data) // num_processes
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

    # Multiprocessing approach
    start_mp = time.time()
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(process_chunk, chunks)
    end_mp = time.time()
    total_mp = sum(results)

    # Single-threaded approach
    start_st = time.time()
    total_st = sum(x * x for x in data)
    end_st = time.time()

    # Print results
    print(f"Number of processes: {num_processes}")
    print(f"Multiprocessed result: {total_mp}, Time: {end_mp - start_mp:.4f}s")
    print(f"Single-threaded result: {total_st}, Time: {end_st - start_st:.4f}s")