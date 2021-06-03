# Maxcut

An implementation of the QAOA algorithm to solve the Max-Cut problem for weighted graphs, 
along with a comparison of this implementation to other approaches for solving the problem,
such as the classical brute-force method quantum annealing using D-Wave solvers.

Note that the Qiskit solution runs on a simulator, not actual quantum hardware.

## File Structure
* The notebook **My_Qiskit_Maxcut.ipynb** explains my implementation of the QAOA algorithm to solve the weighted MaxCut Problem in Qiskit. I originally submitted this notebook as part of the screening task for the [Quantum Open Source Foundation](https://qosf.org)'s mentorship program. 
* The file **MyQAOA.py** contains the functions used for my QAOA implementation in Qiskit. These are the functions that were explained in **My_Qiskit_Maxcut.ipynb**.
* The file **GraphTools.py** contains the Graph class I used to create random weighted graphs for which the Maxcut Problem would be solved. This class also contains the methods which define how to solve the MaxCut problem with D-Wave's Quantum Annealers, as well as how to solve them classically by trying every possible configuration.
* The notebook **Comparison.ipynb** compares the accuracy and runtimes of the D-Wave solution, Qiskit solution, and classical solution. *This is the file that shows the results you may be interested in*.
* The notebook **DWaveVsClassical.ipynb** does a similar comparison for just the D-Wave and classical solution. This shows the results for slightly larger graphs. The Qiskit solution was not included in this file because it was too slow.
* The Images folder contains some images used in the Jupyter notebooks. These images were used to explain my implementation of the QAOA algorithm in Qiskit.

## References

1. Musty Thoughts. https://www.mustythoughts.com/quantum-approximate-optimization-algorithm-explained
2. Musty Thoughts. https://www.mustythoughts.com/vqas-how-do-they-work
3. Jack Ceroni's code: https://lucaman99.github.io/new_blog/2020/mar16.html
4. Ruslan Shaydulin's Tutorial [Part 1]: https://youtu.be/AOKM9BkweVU
5. Ruslan Shaydulin's Tutorial [Part 2]: https://youtu.be/E0Sos_lR-kI
6. Ruslan Shaydulin's Notebook: https://github.com/rsln-s/IEEE_QW_2020
7. D-Wave Tutorial for Maxcut: https://github.com/dwave-examples/maximum-cut
