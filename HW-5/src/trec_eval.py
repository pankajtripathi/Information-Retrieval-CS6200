import math
import sys
import matplotlib.pyplot as plotter
import numpy as np

__author__ = "Pankaj Tripathi"

"""
trec_eval.py
----------
Environment - Python 2.7
Description - Script a program that replicates trec_eval functionality.
              Input : a ranked list file and QREL file, both in TREC format.
              Both files can contain results and assessments for multiple queryIDs.
"""

recalls = (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
cutoffs = (5, 10, 15, 20, 50, 100, 200, 500, 1000)


def readFile(file):
    """
    :param file: name of file to be read in the current working directory
    :return: contents of the file
    """
    try:
        with open(file, 'r') as f:
            return f.read()
    except IOError:
        print "Could not read file " + file
        return None


def calculateDcg(dcg_vector):
    """
    Returns the Discounted Cumulative Gain for given graded relevance judgements.
    :param dcg_vector
    :return: Discounted Cumulative Gain (DCG) value
    """
    dcg_val = 2 ** dcg_vector[0] - 1
    for j in range(1, len(dcg_vector)):
        dcg_val += (2 ** dcg_vector[j] - 1) / math.log(j + 1)
    return dcg_val


def eval_print(qid, ret, rel_docs, rel_ret, prec_at_recalls, avg_prec, prec_at_cutoffs, rec_at_cutoffs, f1_at_cutoffs,
               r_prec, dcg, prec_list, rec_list):
    drawPrecisionCurves(prec_at_recalls, prec_list, rec_list, qid)
    print("\nQueryid (Num):    {0}".format(qid))
    print("Total number of documents over all queries")
    print("    Retrieved:      {0}".format(ret))
    print("    Relevant:       {0}".format(rel_docs))
    print("    Rel_ret:        {0}".format(rel_ret))
    print("Interpolated Recall - Precision Averages:")
    for num in range(len(prec_at_recalls)):
        print("    at {0:.2f}       {1:.4f}".format(recalls[num], prec_at_recalls[num]))
    print("Average precision (non-interpolated) for all rel docs(averaged over queries):")
    print("                  {:.4f}".format(avg_prec))
    print("nDCG (averaged over queries): {:.4f}".format(dcg))
    print("\n    k      Precision@k   Recall@k    F1-Measure@k")
    print("   ===     ===========   ========    ============")
    for num1 in range(len(prec_at_cutoffs)):
        print("{0:4d} docs    {1:.4f}       {2:.4f}        {3:.4f}".format(cutoffs[num1], prec_at_cutoffs[num1],
                                                                           rec_at_cutoffs[num1], f1_at_cutoffs[num1]))
    print("R-Precision (precision after R (= num_rel for a query) docs retrieved):")
    print("    Exact:        {:.4f}".format(r_prec))


def drawPrecisionCurves(precList, prec_list, rec_list, queryNum):
    """
    :param precList: Precision at recall list
    :param queryNum: Each queries
    :return: Precision Recall Curves
    """
    plotter.plot(recalls, precList)
    plotter.plot(rec_list, prec_list)
    plotter.xlabel("Recall")
    plotter.ylabel("Precision")
    plotter.grid(True)
    plotter.title('Precision Recall Curves')
    name = "prec_recall_plot_for_qid_" + str(queryNum+2)
    plotter.savefig(name)
    plotter.close()


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print "Usage:  trec_eval [-q] <qrel_file> <trec_file>\n\n"

    if len(sys.argv) == 3 or len(sys.argv) == 4:
        print_all_flag = False
        qrel_file = sys.argv[1]
        trec_file = sys.argv[2]

        if len(sys.argv) == 4:  # -q option used
            print_all_flag = True
            qrel_file = sys.argv[2]
            trec_file = sys.argv[3]

    qrel_data = readFile(qrel_file)
    trec_data = readFile(trec_file)

    qrel = dict()
    trec = dict()
    num_rel = dict()

    if qrel_data and trec_data:
        if qrel_data != "" and trec_data != "":

            # Ignore the last blank line for both files

            qrel_data = qrel_data.split('\n')[:-1]
            trec_data = trec_data.split('\n')[:-1]

            # values from each line is taken and then kept in a dictionary qrel
            # qrel is a dict, whose keys are query_ids and whose values are
            # another hash. This hash has keys as docIDs and values that are relevance values

            for line in qrel_data:
                (topic, dummy, doc_id, rel) = line.split()
                rel = float(rel)
                if topic in qrel:
                    if doc_id in qrel[topic]:
                        # Update the relevance score with the maximum value
                        qrel[topic][doc_id] = max(qrel[topic][doc_id], rel)
                    else:
                        qrel[topic].update({doc_id: rel})
                else:
                    qrel.update({topic: {doc_id: rel}})

                # Updating the num_rel
                if topic in num_rel:
                    if rel > 0:
                        num_rel[topic] += 1
                else:
                    if rel > 0:
                        num_rel.update({topic: 1})
                    else:
                        num_rel.update({topic: 0})

            # trec = {id: [(docid, score)]}
            for line in trec_data:
                (topic, dummy1, doc_id, dummy2, score, dummy3) = line.split()
                score = float(score)
                if topic in trec:
                    trec[topic].append((doc_id, score))
                else:
                    trec.update({topic: [(doc_id, score)]})

            # sort doc ids for each topics in decreasing order of scores
            trec = {k: sorted(v, key=lambda tup: tup[1], reverse=True) for k, v in trec.iteritems()}

            # Now let's process the data from trec_file to get results.
            num_topics = 0
            sum_prec_at_cutoffs = dict()
            sum_recall_at_cutoffs = dict()
            sum_f1_at_cutoffs = dict()
            sum_prec_at_recalls = dict()
            tot_num_ret = 0
            tot_num_rel = 0
            tot_num_rel_ret = 0
            sum_avg_prec = 0.0
            sum_r_prec = 0.0
            sum_ndcgs = 0.0

            for topic in trec:
                if topic not in num_rel:
                    continue

                num_topics += 1
                href = trec[topic]

                prec_list = list()
                rec_list = list()
                num_ret = 0  # Initialize number retrieved.
                num_rel_ret = 0  # Initialize number relevant retrieved.
                sum_prec = 0  # Initialize sum precision.
                dcg_vector = list()

                # Now sort doc IDs based on scores and calculate stats.
                # Note:  Break score ties lexicographically based on doc IDs.
                # Note2: Explicitly quit after 1000 docs to conform to TREC while still
                #        handling trec_files with possibly more docs.

                for doc_id, score in href:
                    num_ret += 1
                    if doc_id in qrel[topic]:
                        rel = 1 if qrel[topic][doc_id] > 0 else 0
                        dcg_vector.append(rel)
                        sum_prec += rel * (1 + num_rel_ret) / float(num_ret)
                        num_rel_ret += rel
                    else:
                        dcg_vector.append(0)

                    prec_list.append(num_rel_ret / float(num_ret))
                    rec_list.append(num_rel_ret / float(num_rel[topic]))

                    if num_ret >= 1000:
                        break

                avg_prec = sum_prec / float(num_rel[topic])
                # Compute nDCG for the given topic
                if max(dcg_vector) == 0:
                    ndcg = 0.0
                else:
                    ndcg = calculateDcg(dcg_vector) / calculateDcg(sorted(dcg_vector, reverse=True))

                # Fill out the remainder of the precision/recall lists, if necessary.
                final_recall = num_rel_ret / float(num_rel[topic])
                count = num_ret
                while count <= 1000:
                    prec_list.append(num_rel_ret / float(count))
                    rec_list.append(final_recall)
                    count += 1

                # Calculate precision at document cutoff levels.
                prec_at_cutoffs = [prec_list[val] for val in cutoffs]

                # Calculate recall at document cutoff levels.
                recall_at_cutoffs = [rec_list[val] for val in cutoffs]

                # Calculate f1 values at document cutoff levels
                f1_at_cutoffs = list()
                for i in range(len(cutoffs)):
                    a = prec_at_cutoffs[i]
                    b = recall_at_cutoffs[i]
                    if a > 0 and b > 0:
                        f1_at_cutoffs.append((2 * a * b) / float(a + b))
                    else:
                        f1_at_cutoffs.append(0.0)

                # Now calculate R-precision.  We'll be a bit anal here and
                # actually interpolate if the number of relevant docs is not
                # an integer...
                r_prec = 0
                if num_rel[topic] > num_ret:
                    r_prec = num_rel_ret / float(num_rel[topic])
                else:
                    int_num_rel = int(num_rel[topic])  # Integer part.
                    frac_num_rel = num_rel[topic] - int_num_rel  # Fractional part.

                    if frac_num_rel > 0:
                        r_prec = (1 - frac_num_rel) * prec_list[int_num_rel] + frac_num_rel * prec_list[int_num_rel + 1]
                    else:
                        r_prec = prec_list[int_num_rel]

                # Now calculate interpolated precisions...
                max_prec = 0
                for i in range(1000, 0, -1):
                    if prec_list[i] > max_prec:
                        max_prec = prec_list[i]
                    else:
                        prec_list[i] = max_prec

                # Finally, calculate precision at recall levels.
                prec_at_recalls = list()
                i = 1

                for val in recalls:
                    while i <= 1000 and rec_list[i] < val:
                        i += 1
                    if i <= 1000:
                        prec_at_recalls.append(prec_list[i])
                    else:
                        prec_at_recalls.append(0)

                # Print stats on a per query basis if requested.
                if print_all_flag:
                    eval_print(topic, num_ret, num_rel[topic], num_rel_ret, prec_at_recalls, avg_prec, prec_at_cutoffs,
                               recall_at_cutoffs, f1_at_cutoffs, r_prec, ndcg)

                # Now update running sums for overall stats.
                tot_num_ret += num_ret
                tot_num_rel += int(num_rel[topic])
                tot_num_rel_ret += num_rel_ret

                for i in range(0, len(cutoffs), 1):
                    if i in sum_prec_at_cutoffs:
                        sum_prec_at_cutoffs[i] += prec_at_cutoffs[i]
                    else:
                        sum_prec_at_cutoffs[i] = prec_at_cutoffs[i]

                    if i in sum_recall_at_cutoffs:
                        sum_recall_at_cutoffs[i] += recall_at_cutoffs[i]
                    else:
                        sum_recall_at_cutoffs[i] = recall_at_cutoffs[i]

                    if i in sum_f1_at_cutoffs:
                        sum_f1_at_cutoffs[i] += f1_at_cutoffs[i]
                    else:
                        sum_f1_at_cutoffs[i] = f1_at_cutoffs[i]

                for i in range(0, len(recalls), 1):
                    if i in sum_prec_at_recalls:
                        sum_prec_at_recalls[i] += prec_at_recalls[i]
                    else:
                        sum_prec_at_recalls[i] = prec_at_recalls[i]

                sum_avg_prec += avg_prec
                sum_r_prec += r_prec
                sum_ndcgs += ndcg

            # Summary stats
            avg_prec_at_cutoffs = list()
            avg_recall_at_cutoffs = list()
            avg_f1_at_cutoffs = list()
            avg_prec_at_recalls = list()
            newPrecList = list()

            # Now calculate summary stats.
            for i in range(0, len(cutoffs), 1):
                avg_prec_at_cutoffs.append(sum_prec_at_cutoffs[i] / num_topics)
                avg_recall_at_cutoffs.append(sum_recall_at_cutoffs[i] / num_topics)
                avg_f1_at_cutoffs.append(sum_f1_at_cutoffs[i] / num_topics)
            for i in range(0, len(recalls), 1):
                avg_prec_at_recalls.append(sum_prec_at_recalls[i] / num_topics)

            mean_avg_prec = sum_avg_prec / float(num_topics)
            avg_r_prec = sum_r_prec / float(num_topics)
            avg_ndcg = sum_ndcgs / float(num_topics)

            # Print summary stats
            eval_print(num_topics, tot_num_ret, tot_num_rel, tot_num_rel_ret, avg_prec_at_recalls, mean_avg_prec,
                       avg_prec_at_cutoffs, avg_recall_at_cutoffs, avg_f1_at_cutoffs, avg_r_prec, avg_ndcg, prec_list, rec_list)

    else:
        print "One of the files has no content"
