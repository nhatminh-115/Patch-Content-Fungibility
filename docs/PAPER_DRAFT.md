# Patch-Content Fungibility: Geometry, Functional Transmission, and Operator-Aware Token Compression

**Anonymous Authors**  
*Under review*

## Abstract

Vision transformers represent an image as a fixed sequence of patch slots, yet the role of each slot’s image-specific content in late layers remains unclear. We causally replace selected late-layer patch activations with class-agnostic calibration surrogates while preserving token slots, sequence length, model weights, and all subsequent computation. In the tested models, this fixed-slot content replacement reveals conditional fungibility bounded by feature geometry and token diversity, distinct from token pruning or merging. Mechanistic audits associate replaceability with anisotropic downstream transmission, coherent accumulation and cancellation through the attention value path, and a larger functional near-null subspace in later layers. We use an end-to-end downstream Jacobian to define a compression objective and evaluate it on 1,000 held-out images per architecture. At the most aggressive tested budgets, operator-aware variants improve classification accuracy by 4.2–12.0 percentage points over the strongest pruning baseline for each architecture; the accuracy-token frontier shifts on three of four architectures, while a strong merging baseline remains competitive. A separate classifier-carrier study shows that gains in linearized operator space do not reliably improve nonlinear classification or establish a general deployment frontier. The evidence supports a bounded vision-transformer-specific causal chain from fixed-slot patch-content replacement through geometry and coherent functional transmission to downstream compression, with limited translation to practical carrier corrections.

## 1. Introduction

Transformers use self-attention to mix token representations \citep{vaswani2017attention}, while vision transformers (ViTs) represent an image as a sequence of patch embeddings \citep{dosovitskiy2021vit}. Published ViT families include data-efficient supervised training \citep{touvron2021deit}, self-supervised representations \citep{caron2021dino, oquab2024dinov2}, hierarchical attention \citep{liu2021swin}, masked pretraining \citep{he2022mae}, scaling \citep{zhai2022scaling}, training regularization \citep{steiner2022augreg}, and register tokens \citep{darcet2024registers}. Token-reduction methods lower computation by changing which tokens are processed or how they are combined. We ask a different question: when does the remaining network require the image-specific content carried by a late patch slot?

We answer with a controlled content intervention. At a selected late layer, image-specific patch activations are causally removed and replaced with class-agnostic calibration surrogates while token slots, sequence length, model weights, and all downstream computation are held fixed. The intervention isolates content dependence while preserving the structure of the sequence received by later layers. Replaceability is conditional: tolerated content changes depend on feature geometry and token diversity, and this result does not establish that deleting a token is harmless. Fig. 1 maps the intervention to the geometric constraints, anisotropic and coherent transmission, Value-path cancellation, downstream operator, and compression study.
![Figure 1: Fixed-slot patch-content intervention, replacement constraints, and anisotropic transmission](../figures/paper_final_v4/figure1_overview.svg)
*Fig. 1. Conceptual overview of (a) fixed-slot late-layer patch-content substitution, (b) geometry, token-diversity, and Value-path cancellation constraints, and (c) anisotropic downstream transmission. The schematic summarizes the paper’s mechanisms and is not a quantitative result.*

The contribution is the connected ViT-specific causal chain: fixed-slot patch-content substitution, geometric and diversity constraints, Value-mediated coherence and cancellation, downstream-persistent functional transmission, and operator-aware token compression. We do not claim novelty for Jacobians, singular-value decompositions, anisotropy in general, token redundancy, pruning, merging, low-rank operators, or generic output-aware compression. The predictor and practical-carrier branch remains secondary: operator-space improvement is observed, but translation to nonlinear classification and deployment is limited in the measured settings.

## 2. Related Work

Token-reduction methods change the sequence or the computation applied to it. DynamicViT and Expediting Vision Transformers via Token Reorganizations (EViT) score or reorganize tokens \citep{rao2021dynamicvit, liang2022evit}; Token Merging (ToMe) combines similar tokens \citep{bolya2023tome}; A-ViT (Adaptive Tokens for Efficient Vision Transformer) and AdaViT (Adaptive Vision Transformers for Efficient Image Recognition) use adaptive token computation \citep{yin2022avit, meng2022adavit}; and TokenLearner and Token Pooling form smaller, learned or pooled representations \citep{ryoo2021tokenlearner, marin2023tokenpool}. Adaptive Token Sampling (ATS) and Interpretability-Aware Redundancy Reduction (IA-RED²) select tokens using sampling or redundancy criteria \citep{fayyaz2022ats, pan2021iared}. Other approaches include PatchDropout, X-Pruner, and global structural pruning \citep{liu2023patchdropout, yu2023xpruner, yang2023globalvitprune}; joint pruning and squeezing \citep{wei2023tps}; and early-exit pruning for dense prediction \citep{tang2023dtop}. Evo-ViT, Dynamic Grained Encoder, and SPViT adapt token computation or selection \citep{xu2022evovit, song2021dge, kong2022spvit}, while Patch Slimming, Dynamic Transformers, end-to-end sparsity, activation sparsity, and structure-aware pruning explore complementary efficiency settings \citep{tang2022patchslimming, wang2021notallimages, chen2021chasing, chen2023sparsevit, zheng2022savit}. These methods establish strong baselines and context, but alter token count, token identity, or computation. Our Patch-Content Fungibility (PCF) intervention instead changes patch content while preserving slots and downstream computation in the tested causal audit.

Compression by weight or structure pruning has a longer history. Optimal Brain Damage and Optimal Brain Surgeon use sensitivity-based approximations to remove parameters \citep{lecun1989obd, hassibi1993obs}. Later work studies connection pruning, resource-aware pruning, sparse trainable subnetworks, and movement-based pruning \citep{han2015weights, molchanov2017pruning, frankle2019lottery, sanh2020movement}. SparseGPT and Wanda study one-shot pruning of large language models (LLMs), while SliceGPT removes dimensions. Singular value decomposition (SVD) is also used for large-language-model compression in the published SVD-LLM method, which applies a truncation-aware variant \citep{frantar2023sparsegpt, sun2024wanda, ashkboos2024slicegpt, wang2025svdllm}. These works are relevant precedents for compression, but they do not establish the PCF claim or evaluate the fixed-slot patch-content intervention. We use a downstream operator as an empirical objective for grouping and correcting patch carriers; the Jacobian, singular-value decomposition, and output-sensitive objectives themselves are established tools.

Interpretability research cautions that attention weights alone need not explain a model’s decision. Controlled studies examine whether attention is explanation and how explanation changes under interventions \citep{jain2019attentionnotexplanation, serrano2019attentioninterp, wiegreffe2019attentionnotnot}. Attention flow, Integrated Gradients, saliency-map sanity checks, and transformer-specific relevance propagation provide complementary methods for tracing or attributing model behavior \citep{abnar2020attentionflow, sundararajan2017ig, adebayo2018sanity, chefer2021transformerinterp}. Causal abstraction offers a framework for connecting interventions to model-level causal structure \citep{geiger2022causal}. Our evidence uses direct activation interventions and held-out prediction of perturbation damage; it is bounded to the tested models, readouts, and cohorts.

## 3. Experimental Scope and Measurement Units

The paper reports distinct evidence cohorts and keeps their units separate. Table I lists the sampling unit and inference scope for each study. Here, N denotes the count of the stated sampling unit; it is not interchangeable across image-based and perturbation-based studies. Top-1 accuracy means the fraction of evaluated images for which the highest-scoring class equals the ground-truth label.

**TABLE I**

**EVIDENCE COHORTS AND INFERENCE BOUNDARIES**

| Evidence family | Evaluation unit | Calibration/control unit | Inference scope |
|---|---|---|---|
| Attention causal audit | N=100 images | Frozen-attention path controls | Mechanistic evidence only |
| Functional geometry | N=100 images | Threshold-defined subspace analysis | Pilot association only |
| Joint-stream geometry | N=100 images per model | Coherent and sign-varying token patterns | Joint direction/coherence evidence |
| Multi-block operator | N=100 held-out perturbations | Perturbation-level held-out comparison | Damage-prediction association |
| V0.7 activation replacement | N=1,000 images per model | 50% replacement; stated controls | Classifier outcomes for that study |
| Depth-6 follow-up | N=1,000 evaluation images per model | Separate N=1,000-image calibration set per model | Follow-up at the tested layer and replacement fraction |
| V0.9 learned-direction replacement | N=1,000 evaluation images per DeiT model | Disjoint N=1,000-image calibration set per model | Relative learned-versus-random comparison |
| Strict confirmatory compression | N=1,000 held-out images per architecture | Frozen protocol and architecture-specific budgets | Confirmatory classifier result |
| Real classifier-carrier benchmark | N=1,000 held-out images per architecture | Separate full-model timing runs | Classification and measured timing |
| Operator-space carrier experiments | N=100 held-out operator-space images | Separate operator-space calibration/evaluation protocol | Linearized error; no classification claim |

*Table I. Sample units are reported as recorded in each study. Image cohorts are separate unless a source explicitly states otherwise; the multi-block unit counts perturbations, and operator-space carrier results do not measure classification.*

For the intervention, let P_ℓ∈ℝ^{N×D} be the matrix of N patch activations at layer ℓ, and let p_{ℓ,i}∈ℝ^D denote row i. The class-agnostic calibration surrogate for that row is r_{ℓ,i}. The binary indicator m_i is one only for selected slots:
$$
p̃_{ℓ,i}=(1−m_i)p_{ℓ,i}+m_i r_{ℓ,i}, m_i∈{0,1}, i=1,…,N.
$$
Thus, when m_i=0 the original activation remains, and when m_i=1 it is replaced by the corresponding surrogate. The class token, position indices, number of rows, model weights, and subsequent computation remain unchanged. The intervention therefore isolates dependence on image-specific content; it does not test whether deleting a token can be harmless.

For compression, an end-to-end Jacobian locally maps a perturbation of the patch matrix at layer ℓ to the measured downstream readout z. The Jacobian is evaluated at the unperturbed activation; its product with a flattened perturbation gives a first-order prediction of the readout change. The full-J oracle uses a per-example Jacobian and is an offline reference, not a deployable inference procedure. Section 6 defines the operator objective and its grouping variables.

## 4. Late Patch-Content Fungibility Has Geometric and Diversity Boundaries

Across the audited replacement controls, late-layer patch content is more replaceable than early-layer content, but arbitrary substitutions do not preserve function. The original V1 depthwise validation evaluates 1,000 images per architecture under 25% patch replacement. A separately recorded follow-up measured the previously unsampled depth 6 with the same split seeds, replacement fraction, controls, and 1,000-image calibration and evaluation sets for ViT-B/16 AugReg and DINOv2. At depth 6, centroid/Gaussian replacement gives 73.9%/74.9% for ViT-B and 70.6%/74.6% for DINOv2, compared with zero replacement at 71.5%/28.8%; Gaussian values are means over three seeds. Fig. 2 combines that follow-up with the original depths 5, 7, 8, 9, and 10. These results are conditional on the tested models, layer, replacement fraction, calibration distribution, and readout.
![Figure 2: Audited depth-wise replacement controls](../figures/paper_final_v4/figure2_depthwise.svg)
*Fig. 2. Depth-wise replacement accuracy for ViT-B/16 AugReg and DINOv2 under 25% spatial-patch replacement. Original V1 depths are 5, 7, 8, 9, and 10; depth 6 is a separately recorded follow-up. Each evaluation uses N=1,000 images per model. Error bars show Gaussian seed-level standard deviation; dashed lines mark clean accuracy.*

Geometry and diversity constrain replacement. In the separate V0.7 activation-replacement experiment (N=1,000 images per model; 50% replacement), coordinate permutation changes Top-1 accuracy from 66.3% to 52.2% on DeiT-Tiny and from 75.6% to 62.6% on DeiT-Small; sign inversion reduces it to 0.7% and 1.1%, respectively. These are classifier outcomes from the N=1,000 replacement study. A distinct N=100 DeiT-Small operator-space control finds that shuffling principal component analysis (PCA) coordinates increases mean ‖J E‖ by 1.474 (from 6.602 to 8.076); this is linearized operator-space evidence, not Top-1 accuracy. Fig. 3 compares the audited geometry and token-diversity controls.
![Figure 3: Geometry and token-diversity constraints](../figures/paper_final_v4/figure3_geometry_diversity.svg)
*Fig. 3. (a) V1 geometry controls at 50% replacement for ViT-B/16 AugReg and DINOv2 ViT-S/14 compare a calibration centroid, a coordinate-shuffled centroid, and a sign-inverted centroid. (b) The V0.8 grouped-diversity sweep on DeiT-Tiny and DeiT-Small varies K, the number of distinct replacement vectors across all 196 patch positions. Gray dashed lines mark each model’s clean Top-1 accuracy. Bars and line markers show means; dots show recorded runs; error bars show across-seed standard deviation where repeated seeds are available. Each model uses N=1,000 evaluation images and separate calibration data. These are distinct study cohorts, so conditions should be compared within each panel rather than treated as a matched-model contrast.*

V0.8 diversity tests show that low-dimensional variation does not restore full performance and that the tested setting requires high-dimensional structure. In the separate V0.9 study, with 100% patch replacement, N=1,000 evaluation images and a disjoint N=1,000 calibration set per DeiT model, learned low-dimensional variation is more compatible than energy-matched random directions. This relative advantage is model- and amplitude-dependent and does not establish rank-1 sufficiency. Taken together, the interventions support constrained replaceability, not universal interchangeability and not a direct inference that tokens can be deleted at no cost.

## 5. Anisotropic Transmission, Value-Path Cancellation, and End-to-End Geometry

Functional transmission is direction-dependent. In the attention causal audit (N=100 evaluation images), the frozen-attention Value-only path explains 70.8% of the defined coherence-gap margin effect in DeiT-Small and 102.2% in ViT-B. The same path reproduces approximately 97.4% and 99.3% of the immediate readout disturbance, respectively. The ratio above 100% in ViT-B is possible because a secondary contribution partially opposes the Value-path effect. Perturbing patch keys does not change the unperturbed classification-token query in this setup, so the immediate query contribution is zero; key-mediated rerouting remains secondary rather than absent. The frozen-attention algebraic parity check is not independent generalization evidence. Fig. 4 summarizes the audited depth-wise sensitivity pattern, and Fig. 5 compares coherent with sign-varying Value-path transmission.
![Figure 4: Anisotropic functional geometry](../figures/paper_final_v4/figure4_anisotropic_geometry.svg)
*Fig. 4. Ratio between the leading-principal-component and bottom-principal-component sensitivity across depths in the N=100 functional-geometry pilot. The vector diagram is explanatory.*

![Figure 5: Value-path transmission across coherent and sign-varying patch patterns](../figures/paper_final_v4/figure5_value_path_cancellation.svg)
*Fig. 5. Immediate readout disturbance for Value-only and key-plus-value pathways under coherent, random-sign, and checkerboard patterns in two N=100 attention-audit settings.*

With attention weights frozen, the Value-only contribution to the perturbation of readout token i is
$$
Δh_i^{(V)}=W_O\sum_{j=1}^{N}A_{ij}W_Vδx_j.
$$
Here, A_{ij} is the fixed attention weight from patch j to readout i, W_V and W_O are the Value and output projections, and δx_j is the patch perturbation. When attention weights are held fixed, similarly directed patch perturbations can add through the value aggregation, while sign-varying perturbations can partly cancel. This equation describes the audited Value path; it does not claim that the full nonlinear transformer is globally linear or that the Value path is the only causal route.

Local geometry is not sufficient to characterize later readout damage. The multi-block operator study evaluates N=100 held-out perturbations. On these held-out perturbations, damage prediction has higher correlation for the multi-block operator (Pearson r=0.975; Spearman ρ=0.945) than for the single-block operator (r=0.753; ρ=0.735). The mean principal angle from block 8 to block 9 is 49.0 degrees in the reported comparison. Fig. 6 shows this local-versus-end-to-end comparison. Separately, the N=100-image functional-geometry pilot finds that the threshold-defined downstream functional near-null subspace expands with depth while effective functional rank declines in late layers. This is consistent with greater late-layer replacement tolerance measured in separate interventions, but remains an empirical mechanistic association rather than a theorem or universal explanation. A distinct joint-stream geometry audit (N=100 images per model) finds that downstream damage depends jointly on feature direction and token-space coherence: sensitive feature directions are most damaging under coherent token patterns, whereas functionally near-null directions remain comparatively tolerated across the tested patterns.
![Figure 6: Local and end-to-end operator prediction](../figures/paper_final_v4/figure6_end_to_end_operator.svg)
*Fig. 6. Damage-prediction correlation for single-block and end-to-end multi-block operators on 100 held-out perturbations; the diagram summarizes downstream composition, with a 49.0-degree mean principal angle from block 8 to block 9.*

The end-to-end linearization used in this comparison is
$$
J_{ℓ→L}=∂z/∂flat(P_ℓ), Δz≈J_{ℓ→L} flat(ΔP_ℓ).
$$
Here, z is the measured downstream readout, and flat(·) denotes the row-major vectorization used by the implementation. The first expression defines the local Jacobian; multiplying it by a flattened perturbation gives the first-order readout-change approximation in the second expression. This is an empirical model of transmission for the tested perturbations, not an exact identity for large perturbations or a universal explanation of transformer behavior.

## 6. Confirmatory Operator-Aware Token Compression

Strict confirmatory compression uses N=1,000 held-out images per architecture. At each architecture’s most aggressive tested token budget, Table II reports the exact Top-1 comparison among the best pruning baseline, Group Mean, ToMe, the full-J oracle, and its rank-16 and rank-32 approximations. The selected budgets differ by architecture (32 retained tokens for DeiT-Tiny, DeiT-Small, and ViT-B/16; 42 for DINOv2 ViT-S/14), so the rows are within-architecture comparisons rather than a matched token-count experiment. Fig. 7 presents the full accuracy-token curves.

**TABLE II**

**STRICT CONFIRMATORY TOP-1 ACCURACY AT THE MOST AGGRESSIVE TESTED BUDGET**

| Architecture | Budget | Best pruning baseline | Group Mean | ToMe | Full-J oracle | Rank-16 | Rank-32 |
|---|---:|---:|---:|---:|---:|---:|---:|
| DeiT-Tiny | 32 | Random, 58.6% | 66.5% | 65.8% | 67.1% | 67.1% | 67.9% |
| DeiT-Small | 32 | Attention, 71.6% | 76.4% | 76.4% | 75.8% | 76.5% | 76.5% |
| ViT-B/16 | 32 | Random, 69.2% | 73.2% | 73.0% | 74.4% | 73.7% | 74.2% |
| DINOv2 ViT-S/14 | 42 | Random, 61.5% | 72.2% | 69.4% | 73.5% | 73.2% | 73.0% |

*Table II. Top-1 accuracy on N=1,000 held-out images per architecture. The pruning entry is the strongest among Random, Norm, and Attention Pruning at the listed budget. The architecture-specific budgets are the lowest budgets evaluated in the strict confirmatory sweep.*

For each image, N patch tokens are assigned to B carriers. Let S∈{0,1}^{N×B} be the assignment matrix, with exactly one nonzero per row, and let C∈ℝ^{B×D} contain the carrier vectors. The reconstructed patch matrix is P̂=SC. The set G_j contains the patch indices assigned to carrier j, and m_j=|G_j| is its membership count. The Group Mean baseline sets each carrier to the average of the patches assigned to that group:
$$
c_j^{mean}=(1/m_j)Σ_{i∈G_j}p_i, m_j=|G_j|.
$$
The residual matrix E=P−SC contains the difference between the original and reconstructed patches. The operator-aware oracle adjusts the carriers to reduce the Jacobian-predicted effect of this residual on the downstream readout:
$$
C^*=arg min_C ‖J_{ℓ→L} flat(P−SC)‖_2^2 + λ‖P−SC‖_F^2.
$$
The first term penalizes the readout change predicted by the full downstream Jacobian; the second is a trace-scaled Tikhonov penalty that stabilizes the carrier correction. In the implementation, K_j=Σ_{i∈G_j}J_i is the sum of the Jacobian blocks for patches assigned to carrier j, and Σ=Σ_j K_jK_jᵀ/m_j is the group-size-normalized covariance used to scale regularization. The covariance and regularization scale are
$$
K_j=Σ_{i∈G_j}J_i, Σ=Σ_j(K_jK_jᵀ/m_j), λ=10·tr(Σ)/dim(z).
$$
Here, J_i is the Jacobian block for patch i, the sum runs over all B carrier groups, and dim(z) is the readout dimension. Thus the penalty scale follows the trace of the operator-space covariance and the readout dimension. The full-J solution is computed per image and is an offline oracle, not a deployable inference method. Low-rank approximations reduce the operator basis and are evaluated on the same confirmatory cohort.

Across 30,000 method/budget/seed condition rows per architecture, the same 1,000 held-out images are reused across conditions. Operator residual ‖J E‖ is associated with measured logit-L2 distortion: per-architecture Pearson r ranges from 0.739 to 0.866, and Spearman ρ ranges from 0.792 to 0.916. These are condition-level associations, not 120,000 independent images. Rank-16 and rank-32 approximations retain more than 98% of the Group-Mean-to-full-J-oracle compression benefit. This denominator is the benefit from Group Mean to the full-J oracle; it is not an accuracy-recovery ratio, retained spectral energy, practical-predictor recovery, restricted-carrier-oracle recovery, or static-alpha recovery. Fig. 7 reports the confirmatory curves and the audited benefit denominator.
![Figure 7: Confirmatory operator-aware compression and low-rank benefit](../figures/paper_final_v4/figure7_operator_compression.svg)
*Fig. 7. Confirmatory Top-1 accuracy versus retained patch-token fraction for four architectures and the audited rank-16/32 benefit result. The >98% denominator is the Group-Mean-to-full-J-oracle compression benefit, not an accuracy ratio or spectral energy. Each architecture uses N=1,000 held-out images.*

## 7. Carrier-Space Results and Practical Boundary

The separate carrier branch tests whether corrections can be amortized in a compact PCA feature basis. The operator-space experiment uses N=100 held-out operator-space images and does not measure classification. For DeiT-Small at feature dimension q=16, static Feature-PCA recovers 54.91% of the restricted-oracle ‖J E‖ gain. This is operator-space evidence only. Table III reports the corresponding real classifier-carrier results at the selected budgets.

**TABLE III**

**REAL CLASSIFIER-CARRIER COUNTS AT REPORTED BUDGETS**

| Architecture | Budget | Hybrid Group Mean | Static Feature-PCA, q=16 | Static Feature-PCA, q=32 |
|---|---:|---:|---:|---:|
| DeiT-Small | 98 | 764/1,000 (76.4%) | 763/1,000 (76.3%; −0.1 pp) | 760/1,000 (76.0%; −0.4 pp) |
| DeiT-Small | 49 | 755/1,000 (75.5%) | 740/1,000 (74.0%; −1.5 pp) | 740/1,000 (74.0%; −1.5 pp) |
| DINOv2 ViT-S/14 | 42 | 613/1,000 (61.3%) | 568/1,000 (56.8%; −4.5 pp) | 570/1,000 (57.0%; −4.3 pp) |
| ViT-B/16 AugReg | 49 | 712/1,000 (71.2%) | 719/1,000 (71.9%; +0.7 pp) | 716/1,000 (71.6%; +0.4 pp) |

*Table III. Correct predictions out of 1,000 held-out images and Top-1 accuracy for the separate real classifier-carrier benchmark. Parenthetical differences are percentage-point (pp) changes from Hybrid Group Mean at the same architecture and budget. These rows are not the N=100 operator-space experiment.*

The real-final benchmark evaluates actual model predictions on N=1,000 held-out images per architecture. Compact Feature-PCA corrections do not consistently improve classification: both DeiT-Small budgets and the aggressive DINOv2 budget are at or below Hybrid Group Mean, while ViT-B/16 has a limited positive case. Fig. S1 shows the separate full-model throughput boundary; it does not establish a general deployment improvement.
![Figure S1: Measured real carrier accuracy-throughput boundary](../figures/paper_final_v4/supp/figureS1_real_carrier_boundary.svg)
*Fig. S1. Real-final classification and full-model throughput at batch size 64; q=16 has a narrow ViT-B/16 frontier contribution.*

Selective risk gating is also bounded. Its historical operator-space area under the receiver operating characteristic curve (AUROC) is 0.784 and is exploratory; the calibration-frozen real classifier gate does not consistently improve accuracy (DeiT-Small budget 98: 75.8% versus Hybrid Group Mean 76.4%; DINOv2 budget 42: 58.5% versus Hybrid Group Mean 61.3%). For the measured accuracy-throughput frontier, we use only `outputs/fungibility_real_final/real_accuracy_throughput_frontier.csv`: Clean is non-dominated in several regimes, Group Mean is a practical batched baseline, and static q=16 adds a narrow ViT-B/16 point at some batch sizes. q=32 and selective q=16 do not establish a general frontier improvement. Full-call measurements are not isolated operator overhead.

These results distinguish replaceability from compressibility. Single-token carrier attempts fail; scalar layer prediction does not generalize; a compact shared linear envelope with K≤64 captures little of the tested operator subspace; dynamic alpha prediction fails out of sample; and dynamic operator prediction is costly. Static Feature-PCA may improve linearized operator error without improving Top-1 accuracy, while the selective gate has no general deployment-frontier result. These are negative or bounded findings, not another optimization claim.

## 8. Limitations

The mechanism studies are finite: N=100 images for the attention causal audit and functional-geometry pilot, N=100 images per model for joint-stream geometry, and N=100 held-out perturbations for multi-block operator prediction. Their conclusions should not be generalized beyond the tested architectures, layers, perturbations, or readouts. Confirmatory results cover four pretrained vision-transformer families and a specific ImageNet validation subset of N=1,000 held-out images per architecture; broader model and task coverage remains untested. The Jacobian objective is a local linearization, and the full-J oracle requires per-image downstream-Jacobian construction. Real carrier classification shows that reducing linearized error is not sufficient for a deployment gain; measured full-call runtime is also specific to the tested hardware, batch sizes, and implementations and does not isolate operator overhead.

## 9. Conclusion

Late patch activations can be replaceable under constrained geometry and diversity, but that property alone does not imply token deletion or practical acceleration. N=100 mechanism audits connect coherent Value-path transmission and downstream subspace rotation to the need for an end-to-end operator. A strict N=1,000-per-architecture evaluation shows that operator-aware token compression improves over pruning and shifts strong-merging frontiers on three of four architectures, with rank-16/32 retaining more than 98% of the full-J oracle compression benefit. Compact carrier corrections improve operator-space metrics but do not reliably improve classifier accuracy or yield a general measured frontier. This evidence supports a mechanistic result and a bounded constructive compression result, with explicit limits on practical translation.

## Reproducibility and Evidence

The canonical repository is [Patch-Content-Fungibility](https://github.com/nhatminh-115/Patch-Content-Fungibility). Confirmatory compression outputs are in outputs/fungibility_operator_compression_confirmatory/; real classifier-carrier accuracy and full-call timings are in outputs/fungibility_real_final/. The figure and number traceability maps identify source files and sample units. Historical proxy-backed consolidation tables are not empirical support for this manuscript.

## References

```bibtex
@inproceedings{vaswani2017attention, author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N. and Kaiser, Łukasz and Polosukhin, Illia}, title={Attention is All you Need}, booktitle={Advances in Neural Information Processing Systems}, volume={30}, pages={5998--6008}, year={2017}, url={https://proceedings.neurips.cc/paper_files/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html} }

@inproceedings{dosovitskiy2021vit, author={Dosovitskiy, Alexey and Beyer, Lucas and Kolesnikov, Alexander and Weissenborn, Dirk and Zhai, Xiaohua and Unterthiner, Thomas and Dehghani, Mostafa and Minderer, Matthias and Heigold, Georg and Gelly, Sylvain and Uszkoreit, Jakob and Houlsby, Neil}, title={An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale}, booktitle={International Conference on Learning Representations}, year={2021}, url={https://openreview.net/forum?id=YicbFdNTTy} }

@inproceedings{touvron2021deit, author={Touvron, Hugo and Cord, Matthieu and Douze, Matthijs and Massa, Francisco and Sablayrolles, Alexandre and Jégou, Hervé}, title={Training data-efficient image transformers \& distillation through attention}, booktitle={Proceedings of the 38th International Conference on Machine Learning}, series={Proceedings of Machine Learning Research}, volume={139}, pages={10347--10357}, year={2021}, url={https://proceedings.mlr.press/v139/touvron21a.html} }

@inproceedings{caron2021dino, author={Caron, Mathilde and Touvron, Hugo and Misra, Ishan and Jégou, Hervé and Mairal, Julien and Bojanowski, Piotr and Joulin, Armand}, title={Emerging Properties in Self-Supervised Vision Transformers}, booktitle={Proceedings of the IEEE/CVF International Conference on Computer Vision}, pages={9650--9660}, year={2021}, doi={10.1109/ICCV48922.2021.00951}, url={https://openaccess.thecvf.com/content/ICCV2021/html/Caron_Emerging_Properties_in_Self-Supervised_Vision_Transformers_ICCV_2021_paper.html} }

@article{oquab2024dinov2, author={Oquab, Maxime and Darcet, Timothée and Moutakanni, Théo and Vo, Huy and Szafraniec, Marc and Khalidov, Vasil and Fernandez, Pierre and Haziza, Daniel and Massa, Francisco and El-Nouby, Alaaeldin and Assran, Mido and Ballas, Nicolas and Galuba, Wojciech and Howes, Russell and Huang, Po-Yao and Li, Shang-Wen and Misra, Ishan and Rabbat, Michael and Sharma, Vasu and Synnaeve, Gabriel and Xu, Hu and Jégou, Hervé and Mairal, Julien and Labatut, Patrick and Joulin, Armand and Bojanowski, Piotr}, title={DINOv2: Learning Robust Visual Features without Supervision}, journal={Transactions on Machine Learning Research}, year={2024}, url={https://openreview.net/forum?id=a68SUt6zFt} }

@inproceedings{liu2021swin, author={Liu, Ze and Lin, Yutong and Cao, Yue and Hu, Han and Wei, Yixuan and Zhang, Zheng and Lin, Stephen and Guo, Baining}, title={Swin Transformer: Hierarchical Vision Transformer Using Shifted Windows}, booktitle={Proceedings of the IEEE/CVF International Conference on Computer Vision}, pages={10012--10022}, year={2021}, doi={10.1109/ICCV48922.2021.00986}, url={https://openaccess.thecvf.com/content/ICCV2021/html/Liu_Swin_Transformer_Hierarchical_Vision_Transformer_Using_Shifted_Windows_ICCV_2021_paper.html} }

@inproceedings{he2022mae, author={He, Kaiming and Chen, Xinlei and Xie, Saining and Li, Yanghao and Dollár, Piotr and Girshick, Ross}, title={Masked Autoencoders Are Scalable Vision Learners}, booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition}, pages={16000--16009}, year={2022}, doi={10.1109/CVPR52688.2022.01553}, url={https://openaccess.thecvf.com/content/CVPR2022/html/He_Masked_Autoencoders_Are_Scalable_Vision_Learners_CVPR_2022_paper.html} }

@inproceedings{zhai2022scaling, author={Zhai, Xiaohua and Kolesnikov, Alexander and Houlsby, Neil and Beyer, Lucas}, title={Scaling Vision Transformers}, booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition}, pages={12104--12113}, year={2022}, doi={10.1109/CVPR52688.2022.01179}, url={https://openaccess.thecvf.com/content/CVPR2022/html/Zhai_Scaling_Vision_Transformers_CVPR_2022_paper.html} }

@article{steiner2022augreg, author={Steiner, Andreas and Kolesnikov, Alexander and Zhai, Xiaohua and Wightman, Ross and Uszkoreit, Jakob and Beyer, Lucas}, title={How to Train Your ViT? Data, Augmentation, and Regularization in Vision Transformers}, journal={Transactions on Machine Learning Research}, year={2022}, url={https://openreview.net/forum?id=4nPswr1KcP} }

@inproceedings{darcet2024registers, author={Darcet, Timothée and Oquab, Maxime and Mairal, Julien and Bojanowski, Piotr}, title={Vision Transformers Need Registers}, booktitle={International Conference on Learning Representations}, year={2024}, url={https://openreview.net/forum?id=L6T2bA1sJN} }

@inproceedings{rao2021dynamicvit, author={Rao, Yongming and Zhao, Wenliang and Liu, Benlin and Lu, Jiwen and Zhou, Jie and Hsieh, Cho-Jui}, title={DynamicViT: Efficient Vision Transformers with Dynamic Token Sparsification}, booktitle={Advances in Neural Information Processing Systems}, volume={34}, pages={13937--13949}, year={2021}, url={https://proceedings.neurips.cc/paper/2021/hash/747d3443e319a22747fbb873e8b2f9f2-Abstract.html} }

@inproceedings{liang2022evit, author={Liang, Youwei and Ge, Chongjian and Tong, Zhan and Song, Yibing and Wang, Jue and Xie, Pengtao}, title={Not All Patches Are What You Need: Expediting Vision Transformers via Token Reorganizations}, booktitle={International Conference on Learning Representations}, year={2022}, url={https://openreview.net/forum?id=I90fplp5b3} }

@inproceedings{bolya2023tome, author={Bolya, Daniel and Fu, Cheng-Yang and Dai, Xiaoliang and Zhang, Peizhao and Feichtenhofer, Christoph and Hoffman, Judy}, title={Token Merging: Your ViT But Faster}, booktitle={International Conference on Learning Representations}, year={2023}, url={https://openreview.net/forum?id=JroZRaRw7Eu} }

@inproceedings{yin2022avit, author={Yin, Hongxu and Vahdat, Arash and Alvarez, Jose M. and Mallya, Arun and Kautz, Jan and Molchanov, Pavlo}, title={A-ViT: Adaptive Tokens for Efficient Vision Transformer}, booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition}, pages={10809--10818}, year={2022}, doi={10.1109/CVPR52688.2022.01054}, url={https://openaccess.thecvf.com/content/CVPR2022/html/Yin_A-ViT_Adaptive_Tokens_for_Efficient_Vision_Transformer_CVPR_2022_paper.html} }

@inproceedings{meng2022adavit, author={Meng, Lingchen and Li, Hengduo and Chen, Bor-Chun and Lan, Shiyi and Wu, Zuxuan and Jiang, Yu-Gang and Lim, Ser-Nam}, title={AdaViT: Adaptive Vision Transformers for Efficient Image Recognition}, doi={10.1109/CVPR52688.2022.01199}, booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition}, pages={12309--12318}, year={2022}, url={https://openaccess.thecvf.com/content/CVPR2022/html/Meng_AdaViT_Adaptive_Vision_Transformers_for_Efficient_Image_Recognition_CVPR_2022_paper.html} }

@inproceedings{ryoo2021tokenlearner, author={Ryoo, Michael S. and Piergiovanni, AJ and Arnab, Anurag and Dehghani, Mostafa and Angelova, Anelia}, title={TokenLearner: Adaptive Space-Time Tokenization for Videos}, booktitle={Advances in Neural Information Processing Systems}, volume={34}, pages={12786--12797}, year={2021}, url={https://proceedings.neurips.cc/paper/2021/hash/6a30e32e56fce5cf381895dfe6ca7b6f-Abstract.html} }

@inproceedings{marin2023tokenpool, author={Marin, Dmitrii and Chang, Jen-Hao Rick and Ranjan, Anurag and Prabhu, Anish and Rastegari, Mohammad and Tuzel, Oncel}, title={Token Pooling in Vision Transformers for Image Classification}, booktitle={Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision}, pages={12--21}, year={2023}, doi={10.1109/WACV56688.2023.00010}, url={https://openaccess.thecvf.com/content/WACV2023/html/Marin_Token_Pooling_in_Vision_Transformers_for_Image_Classification_WACV_2023_paper.html} }

@inproceedings{fayyaz2022ats, author={Fayyaz, Mohsen and Koohpayegani, Soroush Abbasi and Jafari, Farnoush Rezaei and Sengupta, Sunando and Joze, Hamid Reza Vaezi and Sommerlade, Eric and Pirsiavash, Hamed and Gall, Juergen}, title={Adaptive Token Sampling for Efficient Vision Transformers}, booktitle={Computer Vision -- ECCV 2022}, series={Lecture Notes in Computer Science}, volume={13671}, pages={396--414}, year={2022}, doi={10.1007/978-3-031-20083-0_24}, url={https://link.springer.com/chapter/10.1007/978-3-031-20083-0_24} }

@inproceedings{pan2021iared, author={Pan, Bowen and Panda, Rameswar and Jiang, Yifan and Wang, Zhangyang and Feris, Rogerio and Oliva, Aude}, title={IA-RED²: Interpretability-Aware Redundancy Reduction for Vision Transformers}, booktitle={Advances in Neural Information Processing Systems}, volume={34}, year={2021}, url={https://proceedings.neurips.cc/paper/2021/hash/d072677d210ac4c03ba046120f0802ec-Abstract.html} }

@inproceedings{liu2023patchdropout, author={Liu, Yue and Matsoukas, Christos and Strand, Fredrik and Azizpour, Hossein and Smith, Kevin}, title={PatchDropout: Economizing Vision Transformers Using Patch Dropout}, booktitle={Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision}, pages={3953--3962}, year={2023}, doi={10.1109/WACV56688.2023.00394}, url={https://openaccess.thecvf.com/content/WACV2023/html/Liu_PatchDropout_Economizing_Vision_Transformers_Using_Patch_Dropout_WACV_2023_paper.html} }

@inproceedings{yu2023xpruner, author={Yu, Lu and Xiang, Wei}, title={X-Pruner: eXplainable Pruning for Vision Transformers}, booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition}, pages={24355--24363}, year={2023}, doi={10.1109/CVPR52729.2023.02333}, url={https://openaccess.thecvf.com/content/CVPR2023/html/Yu_X-Pruner_eXplainable_Pruning_for_Vision_Transformers_CVPR_2023_paper.html} }

@inproceedings{yang2023globalvitprune, author={Yang, Huanrui and Yin, Hongxu and Shen, Maying and Molchanov, Pavlo and Li, Hai and Kautz, Jan}, title={Global Vision Transformer Pruning With Hessian-Aware Saliency}, booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition}, pages={18547--18557}, year={2023}, doi={10.1109/CVPR52729.2023.01779}, url={https://openaccess.thecvf.com/content/CVPR2023/html/Yang_Global_Vision_Transformer_Pruning_With_Hessian-Aware_Saliency_CVPR_2023_paper.html} }

@inproceedings{wei2023tps, author={Wei, Siyuan and Ye, Tianzhu and Zhang, Shen and Tang, Yao and Liang, Jiajun}, title={Joint Token Pruning and Squeezing Towards More Aggressive Compression of Vision Transformers}, booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition}, pages={2092--2101}, year={2023}, doi={10.1109/CVPR52729.2023.00208}, url={https://openaccess.thecvf.com/content/CVPR2023/html/Wei_Joint_Token_Pruning_and_Squeezing_Towards_More_Aggressive_Compression_of_CVPR_2023_paper.html} }

@inproceedings{tang2023dtop, author={Tang, Quan and Zhang, Bowen and Liu, Jiajun and Liu, Fagui and Liu, Yifan}, title={Dynamic Token Pruning in Plain Vision Transformers for Semantic Segmentation}, doi={10.1109/ICCV51070.2023.00078}, booktitle={Proceedings of the IEEE/CVF International Conference on Computer Vision}, pages={777--786}, year={2023}, url={https://openaccess.thecvf.com/content/ICCV2023/html/Tang_Dynamic_Token_Pruning_in_Plain_Vision_Transformers_for_Semantic_Segmentation_ICCV_2023_paper.html} }

@article{xu2022evovit, author={Xu, Yifan and Zhang, Zhijie and Zhang, Mengdan and Sheng, Kekai and Li, Ke and Dong, Weiming and Zhang, Liqing and Xu, Changsheng and Sun, Xing}, title={Evo-ViT: Slow-Fast Token Evolution for Dynamic Vision Transformer}, journal={Proceedings of the AAAI Conference on Artificial Intelligence}, volume={36}, number={3}, pages={2964--2972}, year={2022}, doi={10.1609/aaai.v36i3.20202}, url={https://ojs.aaai.org/index.php/AAAI/article/view/20202} }

@inproceedings{song2021dge, author={Song, Lin and Zhang, Songyang and Liu, Songtao and Li, Zeming and He, Xuming and Sun, Hongbin and Sun, Jian and Zheng, Nanning}, title={Dynamic Grained Encoder for Vision Transformers}, booktitle={Advances in Neural Information Processing Systems}, volume={34}, year={2021}, url={https://proceedings.neurips.cc/paper/2021/hash/2d969e2cee8cfa07ce7ca0bb13c7a36d-Abstract.html} }

@inproceedings{kong2022spvit, author={Kong, Zhenglun and Dong, Peiyan and Ma, Xiaolong and Meng, Xin and Niu, Wei and Sun, Mengshu and Shen, Xuan and Yuan, Geng and Ren, Bin and Tang, Hao and Qin, Minghai and Wang, Yanzhi}, title={SPViT: Enabling Faster Vision Transformers via Latency-Aware Soft Token Pruning}, booktitle={Computer Vision -- ECCV 2022}, series={Lecture Notes in Computer Science}, volume={13671}, pages={620--640}, year={2022}, doi={10.1007/978-3-031-20083-0_37}, url={https://link.springer.com/chapter/10.1007/978-3-031-20083-0_37} }

@inproceedings{tang2022patchslimming, author={Tang, Yehui and Han, Kai and Wang, Yunhe and Xu, Chang and Guo, Jianyuan and Xu, Chao and Tao, Dacheng}, title={Patch Slimming for Efficient Vision Transformers}, booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition}, pages={12165--12174}, year={2022}, doi={10.1109/CVPR52688.2022.01185}, url={https://openaccess.thecvf.com/content/CVPR2022/html/Tang_Patch_Slimming_for_Efficient_Vision_Transformers_CVPR_2022_paper.html} }

@inproceedings{wang2021notallimages, author={Wang, Yulin and Huang, Rui and Song, Shiji and Huang, Zeyi and Huang, Gao}, title={Not All Images Are Worth 16x16 Words: Dynamic Transformers for Efficient Image Recognition}, booktitle={Advances in Neural Information Processing Systems}, volume={34}, year={2021}, url={https://proceedings.neurips.cc/paper/2021/hash/64517d8435994992e682b3e4aa0a0661-Abstract.html} }

@inproceedings{chen2021chasing, author={Chen, Tianlong and Cheng, Yu and Gan, Zhe and Yuan, Lu and Zhang, Lei and Wang, Zhangyang}, title={Chasing Sparsity in Vision Transformers: An End-to-End Exploration}, booktitle={Advances in Neural Information Processing Systems}, volume={34}, year={2021}, url={https://proceedings.neurips.cc/paper/2021/file/a61f27ab2165df0e18cc9433bd7f27c5-Abstract.html} }

@inproceedings{chen2023sparsevit, author={Chen, Xuanyao and Liu, Zhijian and Tang, Haotian and Yi, Li and Zhao, Hang and Han, Song}, title={SparseViT: Revisiting Activation Sparsity for Efficient High-Resolution Vision Transformer}, booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition}, pages={2061--2070}, year={2023}, doi={10.1109/CVPR52729.2023.00205}, url={https://openaccess.thecvf.com/content/CVPR2023/html/Chen_SparseViT_Revisiting_Activation_Sparsity_for_Efficient_High-Resolution_Vision_Transformer_CVPR_2023_paper.html} }

@inproceedings{zheng2022savit, author={Zheng, Chuanyang and Li, Zheyang and Zhang, Kai and Yang, Zhi and Tan, Wenming and Xiao, Jun and Ren, Ye and Pu, Shiliang}, title={SAViT: Structure-Aware Vision Transformer Pruning via Collaborative Optimization}, booktitle={Advances in Neural Information Processing Systems}, volume={35}, pages={9010--9023}, year={2022}, doi={10.52202/068431-0655}, url={https://proceedings.neurips.cc/paper_files/paper/2022/hash/3b11c5cc84b6da2838db348b37dbd1a2-Abstract.html} }

@inproceedings{lecun1989obd, author={LeCun, Yann and Denker, John S. and Solla, Sara A.}, title={Optimal Brain Damage}, booktitle={Advances in Neural Information Processing Systems}, volume={2}, pages={598--605}, year={1989}, url={https://proceedings.neurips.cc/paper/1989/hash/6c9882bbac1c7093bd25041881277658-Abstract.html} }

@inproceedings{hassibi1993obs, author={Hassibi, Babak and Stork, David G.}, title={Optimal Brain Surgeon and general network pruning}, booktitle={Proceedings of the IEEE International Conference on Neural Networks}, volume={1}, pages={293--299}, year={1993}, doi={10.1109/ICNN.1993.298572} }

@inproceedings{han2015weights, author={Han, Song and Pool, Jeff and Tran, John and Dally, William J.}, title={Learning Both Weights and Connections for Efficient Neural Networks}, booktitle={Advances in Neural Information Processing Systems}, volume={28}, year={2015}, url={https://proceedings.neurips.cc/paper/2015/hash/ae0eb3eed39d2bcef4622b2499a05fe6-Abstract.html} }

@inproceedings{molchanov2017pruning, author={Molchanov, Pavlo and Tyree, Stephen and Karras, Tero and Aila, Timo and Kautz, Jan}, title={Pruning Convolutional Neural Networks for Resource Efficient Inference}, booktitle={International Conference on Learning Representations}, year={2017}, url={https://openreview.net/forum?id=SJGCiw5gl} }

@inproceedings{frankle2019lottery, author={Frankle, Jonathan and Carbin, Michael}, title={The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks}, booktitle={International Conference on Learning Representations}, year={2019}, url={https://openreview.net/forum?id=rJl-b3RcF7} }

@inproceedings{sanh2020movement, author={Sanh, Victor and Wolf, Thomas and Rush, Alexander M.}, title={Movement Pruning: Adaptive Sparsity by Fine-Tuning}, booktitle={Advances in Neural Information Processing Systems}, volume={33}, pages={20378--20389}, year={2020}, url={https://proceedings.neurips.cc/paper/2020/hash/eae15aabaa768ae4a5993a8a4f4fa6e4-Abstract.html} }

@inproceedings{frantar2023sparsegpt, author={Frantar, Elias and Alistarh, Dan}, title={SparseGPT: Massive Language Models Can Be Accurately Pruned in One-Shot}, booktitle={Proceedings of the 40th International Conference on Machine Learning}, series={Proceedings of Machine Learning Research}, volume={202}, pages={10323--10337}, year={2023}, url={https://proceedings.mlr.press/v202/frantar23a.html} }

@inproceedings{sun2024wanda, author={Sun, Mingjie and Liu, Zhuang and Bair, Anna and Kolter, J. Zico}, title={A Simple and Effective Pruning Approach for Large Language Models}, booktitle={International Conference on Learning Representations}, year={2024}, url={https://openreview.net/forum?id=PxoFut3dWW} }

@inproceedings{ashkboos2024slicegpt, author={Ashkboos, Saleh and Croci, Maximilian L. and Gennari do Nascimento, Marcelo and Hoefler, Torsten and Hensman, James}, title={SliceGPT: Compress Large Language Models by Deleting Rows and Columns}, booktitle={International Conference on Learning Representations}, year={2024}, url={https://openreview.net/forum?id=vXxardq6db} }

@inproceedings{wang2025svdllm, author={Wang, Xin and Zheng, Yu and Wan, Zhongwei and Zhang, Mi}, title={SVD-LLM: Truncation-aware Singular Value Decomposition for Large Language Model Compression}, booktitle={International Conference on Learning Representations}, year={2025}, url={https://proceedings.iclr.cc/paper_files/paper/2025/hash/3104e1ab39875cf54fe1eb4473e7c5a1-Abstract-Conference.html} }

@inproceedings{jain2019attentionnotexplanation, author={Jain, Sarthak and Wallace, Byron C.}, title={Attention Is Not Explanation}, booktitle={Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies}, pages={3543--3556}, year={2019}, doi={10.18653/v1/N19-1357}, url={https://aclanthology.org/N19-1357/} }

@inproceedings{serrano2019attentioninterp, author={Serrano, Sofia and Smith, Noah A.}, title={Is Attention Interpretable?}, booktitle={Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics}, pages={2931--2951}, year={2019}, doi={10.18653/v1/P19-1282}, url={https://aclanthology.org/P19-1282/} }

@inproceedings{wiegreffe2019attentionnotnot, author={Wiegreffe, Sarah and Pinter, Yuval}, title={Attention Is Not Not Explanation}, booktitle={Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing}, pages={11--20}, year={2019}, doi={10.18653/v1/D19-1002}, url={https://aclanthology.org/D19-1002/} }

@inproceedings{abnar2020attentionflow, author={Abnar, Samira and Zuidema, Willem}, title={Quantifying Attention Flow in Transformers}, booktitle={Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics}, pages={4190--4197}, year={2020}, doi={10.18653/v1/2020.acl-main.385}, url={https://aclanthology.org/2020.acl-main.385/} }

@inproceedings{sundararajan2017ig, author={Sundararajan, Mukund and Taly, Ankur and Yan, Qiqi}, title={Axiomatic Attribution for Deep Networks}, booktitle={Proceedings of the 34th International Conference on Machine Learning}, series={Proceedings of Machine Learning Research}, volume={70}, pages={3319--3328}, year={2017}, url={https://proceedings.mlr.press/v70/sundararajan17a.html} }

@inproceedings{adebayo2018sanity, author={Adebayo, Julius and Gilmer, Justin and Muelly, Michael and Goodfellow, Ian and Hardt, Moritz and Kim, Been}, title={Sanity Checks for Saliency Maps}, booktitle={Advances in Neural Information Processing Systems}, volume={31}, pages={9505--9515}, year={2018}, url={https://proceedings.neurips.cc/paper/2018/hash/294a8ed24b1ad22ec2e7efea049b8737-Abstract.html} }

@inproceedings{chefer2021transformerinterp, author={Chefer, Hila and Gur, Shir and Wolf, Lior}, title={Transformer Interpretability Beyond Attention Visualization}, doi={10.1109/CVPR46437.2021.00084}, booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition}, pages={782--791}, year={2021}, url={https://openaccess.thecvf.com/content/CVPR2021/html/Chefer_Transformer_Interpretability_Beyond_Attention_Visualization_CVPR_2021_paper.html} }

@inproceedings{geiger2022causal, author={Geiger, Atticus and Wu, Zhengxuan and Potts, Christopher and Icard, Thomas and Goodman, Noah}, title={Inducing Causal Structure for Interpretable Neural Networks}, booktitle={Proceedings of the 39th International Conference on Machine Learning}, series={Proceedings of Machine Learning Research}, volume={162}, pages={7324--7338}, year={2022}, url={https://proceedings.mlr.press/v162/geiger22a.html} }
```
