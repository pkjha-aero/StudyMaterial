---
title: Detection and segmentation
status: working
tags: [pillar-9, computer-vision, detection, segmentation, yolo]
updated: 2026-09-26
---

# Detection and segmentation

<span class="status status-working">working</span>
<span class="pillar">pillar 9 &middot; Scientific machine learning</span>

!!! abstract "In one minute"
    - Four distinct tasks: **classification, detection, semantic segmentation, instance segmentation** — and the metric differs for each.
    - **mAP is an average over IoU thresholds**, so a single number hides whether your boxes are slightly loose or catastrophically misplaced.
    - **NMS is a post-process with its own hyperparameter**, and it is where crowded scenes fail.
    - One-stage detectors trade a little accuracy for a lot of speed; the gap has narrowed enough that speed usually wins.
    - **Class imbalance is structural in detection** — most anchors are background — which is why focal loss exists.

## Key results

**The four tasks:**

<div class="result" markdown>

| Task | Output | Metric |
|---|---|---|
| Classification | one label per image | accuracy, top-\(k\) |
| Detection | boxes + labels + scores | mAP@\([0.5{:}0.95]\) |
| Semantic segmentation | class per pixel | mIoU |
| Instance segmentation | mask per object | mask AP |
| Panoptic | both, unified | PQ |

</div>

**IoU and mAP:**

\[
\mathrm{IoU} = \frac{|A\cap B|}{|A\cup B|},
\qquad
\mathrm{AP} = \int_0^1 p(r)\,dr,
\qquad
\mathrm{mAP} = \frac{1}{|C|}\sum_{c}\mathrm{AP}_c
\]

COCO-style mAP averages AP over IoU thresholds 0.50 to 0.95 in steps of 0.05. That averaging is why mAP@0.5 and mAP@[0.5:0.95] differ so much: the first accepts loose boxes, the second demands tight ones.

**Architecture families:**

| Family | Structure | Trade |
|---|---|---|
| Two-stage (Faster R-CNN) | propose then classify | accurate, slower |
| One-stage anchor-based (YOLO, SSD, RetinaNet) | dense prediction over anchors | fast |
| Anchor-free (FCOS, CenterNet) | predict centres/distances | simpler, no anchor tuning |
| Transformer (DETR family) | set prediction, bipartite matching | no NMS, slower to converge |
| Promptable (SAM family) | segment anything given a prompt | zero-shot masks, no classes |

**Non-maximum suppression.** Sort by score, keep the highest, drop everything overlapping it above an IoU threshold, repeat. Two failure directions: a high threshold keeps duplicates, a low one deletes genuinely overlapping objects in crowded scenes. Soft-NMS decays scores instead of deleting, which helps crowds.

**Focal loss.** In dense detection, background anchors outnumber foreground by ~1000:1, so cross-entropy is dominated by easy negatives:

\[
\mathrm{FL}(p_t) = -\alpha_t\left(1-p_t\right)^{\gamma}\log(p_t)
\]

\(\gamma\approx2\) down-weights well-classified examples by two orders of magnitude, letting the hard ones drive the gradient.

**Segmentation losses.** Cross-entropy is the baseline; **Dice** \(= 2|A\cap B|/(|A|+|B|)\) directly optimises overlap and handles class imbalance far better. A weighted sum of the two is the common practical choice, particularly for small structures.

**Transfer learning is the norm.** Pretrained backbone, fine-tuned head. Freezing the backbone for the first epochs stabilises training when the new dataset is small.

## Mental model

Detection is a search problem disguised as a regression problem. The model evaluates many candidate locations and scores each; the architecture differences are mostly about how the candidates are generated and how duplicates are removed.

That framing explains the field's direction. Anchors were a way of enumerating candidates by hand, which meant tuning their scales and ratios per dataset. Anchor-free methods generate candidates from the data. Transformer detectors abolish the enumeration entirely by predicting a *set*, which is why they need no NMS — deduplication becomes part of the learned objective rather than a post-process with a threshold.

## Numerics / practice

- **Report mAP at both 0.5 and [0.5:0.95]**, plus per-class AP. The average across classes hides a class that fails completely.
- **Tune the NMS threshold on validation data** for your scene density; the default is tuned for COCO, which may not resemble your imagery.
- **Check the anchor scales against your object sizes** if using an anchor-based detector. Objects far outside the anchor distribution are systematically missed.
- **Use Dice or a compound loss** for segmentation of small or thin structures.

??? warning "Failure modes"
    **mAP quoted without the IoU threshold.** mAP@0.5 and mAP@[0.5:0.95] routinely differ by 20 points on the same model. A number without its threshold is not comparable to anything.

    **NMS deleting real objects in crowds.** Two genuinely overlapping objects — people in a queue, cells in a smear, overlapping vehicles — produce boxes with high mutual IoU, and NMS removes one. Symptom: recall that collapses specifically in dense regions while the overall metric looks acceptable. Soft-NMS or a set-prediction model is the fix.

    **Anchor scales mismatched to object sizes.** A detector configured for COCO-scale objects applied to small distant targets (satellite imagery, surveillance) misses them entirely, and training loss looks unremarkable because the background term dominates. Check the size distribution of your ground truth against the anchors.

    **Pure cross-entropy on imbalanced segmentation.** For a structure occupying 0.5% of the pixels, predicting all-background gives 99.5% pixel accuracy and near-zero loss. The model converges to it. Dice loss is not optional here.

    **Test-set images seen during pretraining.** A backbone pretrained on a large public corpus may have seen your evaluation images if they came from the same source. Rare but real, and it inflates results in a way that is invisible to the usual checks.

    **Train/test distribution shift in acquisition.** Models trained on one camera, one altitude, one season. Performance collapses on a new acquisition and is often misdiagnosed as overfitting to the training set rather than to the *acquisition conditions*.

    **Confidence threshold chosen on the test set.** The operating point is a decision, and picking it by looking at test performance is the leakage described in [evaluation](../ml/evaluation.md).

    <!-- Add your own here. -->

## Worked example

Why the IoU threshold dominates the headline number:

```python
def iou_1d_box(shift, size=100.0):
    """IoU of two equal boxes offset by `shift` along one axis."""
    inter = max(0.0, size - abs(shift))
    union = 2 * size - inter
    return inter / union

print(f"{'offset (px)':>12} {'IoU':>8}   passes@0.5  passes@0.75  passes@0.9")
for shift in (0, 5, 10, 20, 33, 50):
    iou = iou_1d_box(shift)
    print(f"{shift:12d} {iou:8.3f}   {str(iou>=0.5):>10}  {str(iou>=0.75):>11}  {str(iou>=0.9):>10}")
```

```
 offset (px)      IoU   passes@0.5  passes@0.75  passes@0.9
           0    1.000         True         True        True
           5    0.905         True         True        True
          10    0.818         True         True       False
          20    0.667         True        False       False
          33    0.504         True        False       False
          50    0.333        False        False       False
```

A box offset by a third of its width still passes at IoU 0.5. The same box fails every threshold above 0.75. A model reported at mAP@0.5 can be systematically misplacing objects by 30% of their size — which for counting is fine and for measurement is useless.

## Connections

- [Classical CV](classical-cv.md) — the geometry these models do not replace.
- [Scientific imagery](scientific-imagery.md) — detection applied to measurement.
- [DL › Architectures](../dl/architectures.md) — backbones, U-Net, transformers.
- [ML › Evaluation](../ml/evaluation.md) — threshold selection and leakage.

## Sources

- Lin et al. (2017), *Focal Loss for Dense Object Detection*.
- Carion et al. (2020), *End-to-End Object Detection with Transformers*.
- Kirillov et al. (2023), *Segment Anything*.
