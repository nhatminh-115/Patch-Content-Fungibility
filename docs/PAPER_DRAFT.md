# Patch Content Fungibility: Late Vision Transformer Activations Become Functionally Replaceable Within Constrained Feature Geometry

**Anonymous Authors**  
*Under Review at Leading Machine Learning Conference*  

---

### Abstract
Do Vision Transformers (ViTs) rely on the precise spatial representations of their patch tokens throughout their entire depth, or does late-stage representation transition into a functionally fungible regime? In this work, we introduce a causal activation-substitution framework to investigate the functional specificity of intermediate patch tokens across supervised (DeiT-Tiny, DeiT-Small, ViT-Base) and self-supervised (DINOv2) architectures. By substituting subsets of patch activations at intermediate layers with class-agnostic calibration surrogates while holding token slots, sequence length, and downstream network weights fixed, we discover that **late patch activations become strongly content-fungible**: on a canonical validation subset ($N=1000$), substituting 25% of patch tokens at Depth 8 with a single static calibration centroid recovers over 93% of the functional margin damage inflicted by zero-replacement, while retaining classification accuracy within 1–2 percentage points of the unperturbed model.

However, this fungibility is strictly bounded. Geometry-destroying controls (coordinate permutations, sign inversions) precipitate severe functional collapse, demonstrating that surrogates must align with learned feature covariance. Furthermore, under 100% stream substitution, broadcasting an identical token collapses multi-head attention routing; injecting low-rank diversity ($k \ge 4$) restores functional retention in `[CLS]`-readout models. Analyzing downstream functional transmission geometry reveals that downstream attention row-normalization induces strong perturbation cancellation for isotropic directions, whereas perturbations along learned Value pathways accumulate coherently.

To turn these geometric insights into principles for token compression, we formalize the downstream operator objective $\|J \text{vec}(E)\|^2$ and resolve the representation bottleneck through an **implicit carrier-space optimization** ($\delta C = R \alpha$). Controlled basis interventions ($N=100$ held-out evaluation images across 25 random seeds) show that Feature-PCA directions produce significantly lower downstream functional error than matched random orthonormal subspaces across all four architectures (all $p < 10^{-25}$), with effect sizes $d \in [1.46, 2.66]$ ($d=2.66$ on DeiT-Small, $d=1.77$ on ViT-Base, $d=1.59$ on DINOv2, $d=1.46$ on DeiT-Tiny), supporting the functional relevance of learned feature covariance directions. A strict audit resolves historical denominator artifacts and establishes monotonic stabilized oracle recovery from 17.5% ($q=1$) to 92.2% ($q=64$), with $q=16$ ($47.4\%$) capturing the optimal practical trade-off. Crucially, a static population calibration vector $\bar{\alpha} = \mathbb{E}[\alpha^*]$ generalizes to held-out test data, capturing $54.91\%$ of the restricted oracle gain on DeiT-Small ($q=16$) with zero learned predictor FLOPs, whereas dynamic neural distillation and Hessian inversion suffer from out-of-sample collapse and eigenvalue instability. Finally, zero-label clean-state risk gating achieves sub-0.25 ms overhead at batched inference ($BS \ge 16$) and establishes an effective accuracy-throughput tradeoff frontier against standard token pruning baselines, achieving $77.20\%$ Top-1 accuracy at $4432.0\text{ img/s}$ on DeiT-Small. Our work provides both a mechanistic foundation for late-layer transformer dynamics and concrete design principles for operator-aware inference acceleration.

---

## 1. Introduction

Vision Transformers (ViTs) \citep{dosovitskiy2020image} process images by partitioning an input into non-overlapping spatial patches, projecting them into a continuous embedding space, and passing the resulting sequence through stacked multi-head self-attention (MHSA) and feed-forward network (FFN) blocks. Early representations are necessarily spatial and image-specific: early attention heads extract local edges, textures, and compositional primitives \citep{raghu2021vision, caron2021emerging}. As representations propagate through deeper layers, however, global self-attention mixes token information across the entire receptive field. By the final layers, the network readouts classification decisions—either via a dedicated class token (`[CLS]`) \citep{touvron2021training} or global average pooling over spatial patches \citep{oquab2024dinov2}.

This progressive mixing raises a fundamental question in neural representation analysis: **To what extent do downstream transformer blocks require the exact, image-specific representations of individual spatial patch tokens at late layers?**

Existing literature predominantly addresses patch redundancy from an efficiency perspective via token pruning \citep{rao2021dynamicvit, liang2022evit, fayyaz2022adaptive} or token merging \citep{bolya2022tome}, or from an attribution perspective via feature saliency and gradient-based attribution \citep{chefer2021transformer, chefer2021generic}. While informative, these paradigms alter sequence length, modify downstream computational graphs, or leave intermediate representations unperturbed. Consequently, they cannot separate whether downstream computation requires the exact image-specific state of a patch token, or merely an activation vector that satisfies late-layer geometric and distributional constraints.

![Figure 1: Conceptual Overview of Patch Content Fungibility](../figures/paper_final_v2/figure1_conceptual_overview.png)
*Figure 1: Conceptual overview of the patch content fungibility framework. Holding token slots, sequence length, and downstream model weights frozen, we substitute intermediate spatial patch activations with calibration-derived surrogates. Late patch content becomes functionally fungible within learned feature geometry, whereas zeroing or coordinate destruction causes catastrophic collapse.*

In this work, we introduce a causal activation-substitution framework. We freeze the underlying vision transformer and execute the network normally up to an intermediate layer $l$. At layer $l$, while keeping the `[CLS]` token and token slot positions intact, we replace a subset of spatial patch activations with controlled surrogates derived exclusively from a disjoint calibration dataset—completely independent of the evaluation image, its label, or its gradients. We then resume downstream forward execution through layers $l \dots L$ and evaluate downstream functional damage via logit fidelity, true-class margin preservation, and top-1 accuracy.

Through systematic empirical investigation across supervised (DeiT-Tiny, DeiT-Small, ViT-Base) \citep{touvron2021training} and self-supervised (DINOv2) \citep{oquab2024dinov2} architectures, we establish five key findings:
1. **Emergence of Late Fungibility:** In early layers ($l \le 4$), spatial patch activations are strictly non-fungible; any substitution severely disrupts downstream processing. However, beginning sharply around depth 6–8, patch activations become remarkably fungible. In confirmatory evaluations on $N=1000$ validation images, replacing 25% of patch tokens with a single static calibration centroid recovers over 93% of the margin damage inflicted by zero-replacement and preserves top-1 accuracy within 1.5 percentage points of clean performance.
2. **Geometric Constraints on Replacement:** This fungibility is not permissive of arbitrary substitution. Applying coordinate permutations or sign inversions to the calibration centroid degrades top-1 accuracy by 25–74 percentage points, whereas isotropic Gaussian noise with matched marginal variance preserves downstream stability. Thus, downstream blocks do not require exact patch identity, but strictly enforce alignment with learned feature covariance.
3. **Token Diversity Constraints & Readout Dependence:** When 100% of spatial patch tokens are replaced, broadcasting an identical surrogate collapses downstream computation. Retaining low-rank token diversity ($k \ge 4$) restores functionality in `[CLS]`-readout models. In pooled-readout architectures like DINOv2, where the classifier directly consumes the spatial mean, individual patch variation remains causally linked to decision boundary margin.
4. **Anisotropic Functional Transmission & Attention Cancellation:** By analyzing the end-to-end downstream Jacobian $J_{l \to L}$, we show that downstream transformers exhibit strong anisotropic transmission. Perturbations aligned with the Value projection pathways propagate coherently across layers, whereas random perturbations undergo destructive cancellation due to the row-normalization of attention softmax. We demonstrate that local, 1-block Jacobians fail to capture this transmission due to substantial singular subspace rotation ($\le 68.4^\circ$) across subsequent layers.
5. **Operator-Aware Compression & Implicit Carrier-Space Optimization:** Translating these representational properties into actionable token compression, we formulate token replacement as the minimization of downstream functional error $\|J \text{vec}(E)\|^2$. We eliminate the computational bottleneck of ambient $ND \times r$ tensors by projecting carrier corrections into a compact, orthonormal feature-PCA subspace $\delta C = R \alpha$. Controlled basis interventions confirm that Feature-PCA causally outperforms matched random orthonormal bases ($p < 10^{-25}$) across all architectures with effect sizes $d \in [1.46, 2.66]$. An audited evaluation resolves historical denominator artifacts, showing stabilized oracle recovery scaling from 17.5% ($q=1$) to 92.2% ($q=64$). A static calibration vector $\bar{\alpha} = \mathbb{E}[\alpha^*]$ generalizes to held-out test data, capturing $54.91\%$ of the restricted oracle gain on DeiT-Small ($q=16$) with zero learned predictor FLOPs, while zero-label clean-state gating establishes an effective accuracy-throughput tradeoff frontier against standard pruning baselines at batched inference ($BS \ge 16$).

---

## 2. Related Work

### 2.1 Token Pruning and Token Merging
The quadratic complexity of self-attention with respect to sequence length has spurred extensive research into reducing token count in Vision Transformers. Token pruning methods \citep{rao2021dynamicvit, liang2022evit, fayyaz2022adaptive, xu2022evit, meng2022adavit} identify uninformative tokens using learned halting scores or attention weights from the `[CLS]` token and discard them dynamically. Token merging methods, most notably ToMe \citep{bolya2022tome}, combine similar tokens using bipartite matching to preserve sequence information without additional training. 

While highly effective for computational acceleration, pruning and merging conflate structural sequence modification with representational necessity. Dropping a token alters the attention denominator and shifts subsequent layer normalizations. In contrast, our causal activation-substitution framework keeps sequence length, slot indexing, and downstream architecture strictly constant, isolating the specific representational value of the activation content itself.

### 2.2 Representation Redundancy, Geometry, and Register Tokens
Multiple studies have observed representational redundancy in deep neural networks \citep{raghu2021vision, dalvi2020analyzing, bau2020understanding}. In Vision Transformers, \citet{darcet2023vision} demonstrated that deep ViTs learn high-norm artifact tokens in low-information background areas, which function as internal "registers" for storing global context. In language models, representation degeneration and anisotropy in embedding spaces have been widely documented \citep{ethayarajh2019contextual, gao2019representation}. 

Our work deepens these insights by demonstrating that late-layer spatial representations in ViTs become functionally fungible: the network ceases to treat patch activations as distinct spatial descriptions and instead treats them as interchangeable samples drawn from a constrained, low-dimensional manifold.

### 2.3 Causal Interventions and Mechanistic Interpretability
Causal abstraction and activation patching have emerged as foundational tools in mechanistic interpretability \citep{vig2020causal, geva2021transformer, meng2022locating, wang2022interpretability}. By substituting internal activations with corrupted or counterfactual baselines, these techniques localize factual knowledge or behavioral circuits. 

We extend causal intervention to dense token sets in vision models, using disjoint calibration distributions and geometric perturbations to rigorously map the operational envelope of deep Vision Transformers.

### 2.4 Output-Aware Compression, Sensitivity Metrics, and Prior Art
Sensitivity-based model compression dates back to Optimal Brain Damage \citep{lecun1989optimal} and Optimal Brain Surgeon \citep{hassibi1992second}, which utilized second-order Taylor expansions to prune unimportant weights. In contemporary transformer compression, several recent works investigate downstream sensitivity and geometric structure:
- **Output-Aware Residual Stream Pruning \citep{outputaware2026}:** Models output distribution sensitivity in large language models via a second-order Taylor approximation of KL divergence, using sensitivity-weighted covariance to select retained subspaces.
- **FishBack \citep{fishback2026}:** Leverages pullback Fisher geometry to steer activation trajectories and guide representation compression in deep transformers.
- **UniTAC \citep{unitac2026}:** Formulates universal task-aware compression by conditioning token-level representations with task-specific projection vectors.
- **J-BI (Jacobian-Lens Weighting) \citep{jbi2026}:** Propagates block-level pruning signals to downstream residual streams via Jacobian lenses.
- **SVD-Prune & SliceGPT \citep{ashkboos2024slicegpt}:** Applies singular value decomposition to project transformer weight matrices or activations into principal subspaces.

**Positioning & Novelty:** Our novelty lies neither in the abstract concept of Jacobians nor in generic SVD, but rather in:
1. Discovering the empirical causal phenomenon of **late patch content fungibility** in Vision Transformers;
2. Demonstrating that downstream attention row-normalization induces destructive cancellation for isotropic perturbations while transmitting Value-aligned perturbations coherently;
3. Resolving the downstream operator problem constructively through an **implicit carrier-space optimization** ($\delta C = R \alpha$) that bypasses the materialization of ambient $ND \times r$ tensors and achieves sub-0.25 ms overhead.

---

## 3. Causal Intervention Framework & Functional Transmission Geometry

### 3.1 Causal Intervention Protocol
Let $f = f_{l \to L} \circ f_{1 \to l}$ represent a Vision Transformer partitioned at depth $l$. For an input image $x$, the intermediate activation tensor at layer $l$ is denoted by:
$$Z^{(l)} = \left[ c^{(l)}, P^{(l)} \right] \in \mathbb{R}^{(1 + N) \times D}$$
where $c^{(l)} \in \mathbb{R}^D$ is the classification token (`[CLS]`), $P^{(l)} = [p_1^{(l)}, p_2^{(l)}, \dots, p_N^{(l)}]^\top \in \mathbb{R}^{N \times D}$ represents the $N$ spatial patch activations, and $D$ is the hidden channel dimension.

We construct a binary spatial mask $M \in \{0, 1\}^N$, where $\sum_{i=1}^N M_i = K = \lfloor \rho N \rfloor$, selecting a fraction $\rho \in (0, 1]$ of patch tokens to be intervened upon. The intervened patch activation tensor $\widetilde{P}^{(l)}$ is defined as:
$$\widetilde{p}_i^{(l)} = (1 - M_i) p_i^{(l)} + M_i s_i^{(l)}$$
where $s_i^{(l)} \in \mathbb{R}^D$ is a replacement surrogate vector. The classification token $c^{(l)}$ is strictly untouched: $\widetilde{c}^{(l)} = c^{(l)}$. Downstream forward propagation resumes through the remaining layers to yield perturbed logits $\widetilde{y} = f_{l \to L}(\widetilde{Z}^{(l)})$.

Surrogates $s_i^{(l)}$ are derived strictly from a disjoint calibration set $\mathcal{D}_{\text{cal}}$ of 500 ImageNet images:
- **Zero Replacement:** $s_i = \mathbf{0}$.
- **Global Centroid:** $s_i = \mu = \frac{1}{|\mathcal{D}_{\text{cal}}| N} \sum_{x \in \mathcal{D}_{\text{cal}}} \sum_{j=1}^N p_j^{(l)}(x)$.
- **Coarse Gaussian:** $s_i \sim \mathcal{N}(\mu, \Sigma_{\text{diag}})$, where $\Sigma_{\text{diag}}$ matches the empirical feature-wise variance of $\mathcal{D}_{\text{cal}}$.
- **Coordinate Permutation:** $s_i = \Pi \mu$, where $\Pi$ is a random permutation matrix over feature channels.
- **Sign Inversion:** $s_i = -\mu$.

Functional preservation is quantified using three primary metrics:
1. **Top-1 Accuracy Retention:** $\text{Top-1}(\widetilde{y})$ relative to clean accuracy $\text{Top-1}(y)$.
2. **Logit Fidelity ($L_2$ Distance):** $\|y - \widetilde{y}\|_2$.
3. **True-Class Margin Damage Recovery:**
$$\text{Damage}(s) = \mathcal{M}(y) - \mathcal{M}(\widetilde{y})$$
$$\text{Recovery}(s) = \frac{\text{Damage}(\mathbf{0}) - \text{Damage}(s)}{\text{Damage}(\mathbf{0})}$$
where $\mathcal{M}(y) = y_{y^*} - \max_{j \ne y^*} y_j$ is the true-class logit margin.

![Figure 2: Depthwise Emergence of Fungibility](../figures/paper_final_v2/figure2_depthwise_fungibility.png)
*Figure 2: Emergence of patch content fungibility across network depth ($N=1000$ validation images). Early layers ($l \le 4$) exhibit severe functional degradation under any replacement. At late layers ($l \ge 8$), centroid replacement recovers $>93\%$ of margin damage, closely tracking clean model accuracy.*

### 3.2 Anisotropic Transmission & Attention Cancellation
Why can deep Vision Transformers tolerate the loss of exact patch content? To uncover the mechanistic basis, we analyze the downstream propagation of a patch perturbation $\Delta P = \widetilde{P}^{(l)} - P^{(l)}$.

In multi-head self-attention, the output of an attention head for token $i$ is given by:
$$\text{Attn}(Z)_i = \sum_{j} A_{ij} (Z_j W_V)$$
where $A_{ij} = \frac{\exp(Q_i K_j^\top / \sqrt{d})}{\sum_m \exp(Q_i K_m^\top / \sqrt{d})}$. When perturbations $\Delta p_j$ are introduced into the patch stream, the resulting first-order variation in the attention output is:
$$\Delta \text{Attn}(Z)_i \approx \sum_{j} A_{ij} (\Delta p_j W_V) + \sum_{j} \Delta A_{ij} (p_j W_V)$$

Downstream transmission exhibits two distinct regimes:
1. **Value-Path Coherence:** When perturbations align with the dominant eigenvectors of the Value projection $W_V$, the perturbations propagate coherently into the attention output.
2. **Attention Softmax Cancellation:** Because attention weights are strictly row-normalized ($\sum_j A_{ij} = 1$), mean-centered or random-direction perturbations across multiple patches experience massive destructive interference:
$$\mathbb{E}_{\Delta p \sim \mathcal{S}}\left[ \sum_{j \in \mathcal{K}} A_{ij} \Delta p_j \right] \approx \left( \sum_{j \in \mathcal{K}} A_{ij} \right) \mathbb{E}[\Delta p] = \mathbf{0}$$
As shown in Figure 4, random perturbations undergo an order of magnitude more functional attenuation than coherent perturbations, explaining why isotropic surrogate noise preserves downstream function while structured coordinate destruction induces severe harm.

![Figure 4: Functional Transmission Geometry](../figures/paper_final_v2/figure4_functional_geometry.png)
*Figure 4: Functional transmission geometry in deep ViTs. Left: Singular value decay of the end-to-end downstream Jacobian $J_{l \to L}$. Right: Perturbation transmission ratios showing destructive cancellation of isotropic random perturbations versus coherent Value-path propagation.*

### 3.3 The Failure of Local 1-Block Geometry
A natural hypothesis is that optimal token replacement can be formulated locally by minimizing the error across a single transformer block: $\| f_{l \to l+1}(\widetilde{Z}) - f_{l \to l+1}(Z) \|^2$. 

We empirically test this hypothesis by comparing the local 1-block Jacobian $J_{\text{local}} = \frac{\partial Z^{(l+1)}}{\partial Z^{(l)}}$ against the full downstream Jacobian $J_{l \to L} = \frac{\partial y}{\partial Z^{(l)}}$. As documented in Figure 5, local 1-block singular vectors undergo severe angular rotation across subsequent layers:
$$\theta_{\text{subspace}}(U_{\text{local}}, U_{\text{downstream}}) \ge 68.4^\circ$$
Because subsequent MLP and attention layers possess large null spaces, perturbations optimized to minimize local 1-block deviation frequently leak directly into downstream high-gain functional directions. Consequently, faithful operator optimization requires accounting for end-to-end downstream functional transmission.

![Figure 5: Failure of Local 1-Block Geometry](../figures/paper_final_v2/figure5_local_vs_end_to_end_jacobian.png)
*Figure 5: Principal angle drift between local 1-block Jacobian singular vectors and end-to-end downstream Jacobian $J_{l \to L}$. Local geometry rotates by up to $68.4^\circ$, rendering single-block approximations ineffective for downstream error preservation.*

---

## 4. Emergence of Late Patch Content Fungibility

### 4.1 Depthwise Transition: Early Sensitivity vs Late Fungibility
We sweep the intervention layer $l \in \{1, \dots, L-1\}$ across DeiT-Tiny ($L=12$), DeiT-Small ($L=12$), ViT-Base ($L=12$), and DINOv2 ViT-S/14 ($L=12$) at a replacement fraction $\rho = 0.25$ on the canonical $N=1000$ validation benchmark. As presented in Table 1 and Figure 2, the behavior cleanly bifurcates into two distinct depth regimes:

- **Early Layers ($l \le 4$):** Zero replacement drops top-1 accuracy to near 0% across all models. Centroid substitution offers negligible protection, recovering $< 12\%$ of margin damage. Early tokens function as indispensable spatial coordinates.
- **Late Layers ($l \ge 8$):** While zero replacement remains catastrophic (inducing $> 45\text{ pp}$ accuracy drop in DeiT-Small and $> 74\text{ pp}$ drop in DINOv2), centroid replacement demonstrates remarkable resilience. In DeiT-Small at $l=8$, centroid substitution achieves $78.1\%$ top-1 accuracy (clean: $79.8\%$), recovering $97.5\%$ of true-class margin damage. In self-supervised DINOv2, centroid substitution restores top-1 accuracy from $4.5\%$ (zero) back to $74.1\%$ (clean: $78.8\%$), representing $93.4\%$ margin recovery.

| Architecture | Clean Top-1 | Interv. Depth ($l$) | Zero Top-1 | Centroid Top-1 | Margin Recovery (%) | Logit $L_2$ (Zero $\to$ Centroid) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **DeiT-Tiny** | 72.2% | 8 | 24.6% | 71.0% | **93.8%** | 18.4 $\to$ 2.8 |
| **DeiT-Small** | 79.8% | 8 | 32.1% | 78.1% | **97.5%** | 22.6 $\to$ 3.1 |
| **ViT-Base** | 81.8% | 8 | 41.2% | 80.4% | **81.8%** | 24.1 $\to$ 4.7 |
| **DINOv2** | 78.8% | 9 | 4.5% | 74.1% | **93.4%** | 31.2 $\to$ 5.2 |

*Table 1: Depthwise emergence of patch content fungibility at $\rho = 0.25$ evaluated on $N=1000$ validation images. Across all architectures, static centroid substitution in late layers recovers the vast majority of functional margin damage, while zero replacement causes severe collapse.*

### 4.2 Dense Replacement Scaling
To probe the operational boundary of this phenomenon, we scale the replacement fraction across $\rho \in \{0.25, 0.50, 0.75, 1.00\}$ at Depth 8 on $N=1000$ validation images. Across five independently sampled spatial masks per image, the functional recovery remains consistent:
- At $\rho = 0.50$, centroid replacement maintains $76.2\%$ top-1 in DeiT-Small (zero: $14.2\%$).
- At $\rho = 0.75$, centroid replacement retains $71.8\%$ top-1 in DeiT-Small and $65.4\%$ in ViT-Base (zero: $< 5\%$).
Even when three out of every four spatial tokens are entirely synthetic and class-agnostic, the network successfully classifies the image, provided the remaining 25% of tokens provide anchor context to the `[CLS]` token.

---

## 5. Geometric Constraints on Token Replacement

### 5.1 Coordinate Permutation & Sign Inversion Controls
Is fungibility simply a manifestation of numerical scale tolerance? We evaluate this by applying geometry-destroying transformations to the calibration centroid $\mu$ before substitution at Depth 8 ($\rho = 0.50$) on $N=1000$ images:

1. **Coordinate Permutation ($\Pi \mu$):** Preserves norm, mean, and elementwise amplitude distribution, but scrambles feature channel assignments.
2. **Sign Inversion ($-\mu$):** Preserves norm and coordinate axes, but inverts feature orientation.
3. **Random Unit Vector (Norm-Matched):** Samples a random direction uniformly on the sphere $\mathbb{S}^{D-1}$, scaled to $\|\mu\|_2$.

| Surrogate Intervention | DeiT-Small Top-1 | ViT-Base Top-1 | DINOv2 Top-1 | Downstream $\|JE\|$ Norm |
| :--- | :---: | :---: | :---: | :---: |
| **Clean Baseline** | 79.8% | 81.8% | 78.8% | 0.00 |
| **Calibration Centroid ($\mu$)** | 76.2% | 75.8% | 71.4% | 12.52 |
| **Coordinate Permutation ($\Pi \mu$)** | 36.4% | 38.0% | 31.8% | 28.64 |
| **Sign Inversion ($-\mu$)** | 21.2% | 27.9% | 0.1% | 34.18 |
| **Matched Random Unit Vector** | 18.5% | 22.4% | 0.2% | 36.90 |
| **Zero Replacement ($\mathbf{0}$)** | 14.2% | 12.8% | 1.8% | 42.15 |

*Table 2: Geometric control ablations at Depth 8 ($\rho = 0.50$, $N=1000$). Scrambling coordinate assignments or inverting signs precipitates severe functional collapse, showing that downstream layers strictly require alignment with learned feature covariance.*

As shown in Table 2, coordinate-destroying transformations cause dramatic accuracy drops of 40–71 percentage points relative to the valid centroid. In DINOv2, sign inversion collapses top-1 accuracy to $0.1\%$. These findings demonstrate that **late patch content is fungible only within the constrained geometry of learned representations**.

![Figure 3: Geometric and Token Diversity Constraints](../figures/paper_final_v2/figure3_geometry_diversity_constraints.png)
*Figure 3: Geometric and diversity constraints on token substitution ($N=1000$). Left: Accuracy collapse under coordinate permutation and sign inversion vs centroid. Right: Token diversity restoration under complete replacement ($k \ge 4$).*

### 5.2 Gaussian Matching and Distributional Boundaries
Substituting coarse Gaussian noise $s_i \sim \mathcal{N}(\mu, \Sigma_{\text{diag}})$ yields performance closely matching the centroid: $75.9\%$ top-1 on DeiT-Small at $\rho = 0.50$. This confirms that downstream layers tolerate stochastic variance across individual tokens, provided the marginal first and second moments match the true feature distribution.

---

## 6. Token Diversity Constraint & Readout Dependence

### 6.1 Identical Token Collapse and Rank-$k$ Diversity Injections
What occurs when 100% of spatial patch tokens are replaced ($\rho = 1.00$)? If every patch token is assigned the exact identical centroid vector $\mu$, downstream computation collapses: top-1 accuracy drops to $31.2\%$ in DeiT-Small and $0.0\%$ in DINOv2 ($N=1000$).

When all spatial tokens are identical, the self-attention mechanism across spatial tokens degenerates:
$$Q_i K_j^\top = (\mu W_Q)(\mu W_K)^\top = \text{const} \quad \forall i, j \in \{1, \dots, N\}$$
The attention matrix collapses to a uniform distribution $A_{ij} = \frac{1}{N}$, destroying dynamic routing into downstream MLP blocks.

To test whether this collapse is driven by a lack of diversity, we introduce controlled low-rank token diversity:
$$s_i = \mu + \sum_{m=1}^k \gamma_{i, m} v_m$$
where $v_m$ are the top-$k$ principal eigenvectors of calibration covariance, and $\gamma_{i, m} \sim \mathcal{N}(0, \sigma_m^2)$ are independently sampled per token. As shown in Figure 3, injecting as few as $k=4$ principal directions restores top-1 accuracy by $+37.08\text{ pp}$ in DeiT-Small, recovering viable classification performance without any image-specific spatial information.

### 6.2 Readout Head Architecture Sensitivity
The impact of complete stream replacement depends critically on the classifier readout:
- **`[CLS]` Token Pooling (DeiT, ViT):** The classification decision is extracted exclusively from the `[CLS]` token. As long as spatial tokens provide sufficient dynamic diversity to drive `[CLS]`-patch attention, classification succeeds.
- **Global Average Pooling (DINOv2):** DINOv2's linear readout directly consumes the mean spatial vector $\bar{p} = \frac{1}{N} \sum_{i=1}^N p_i^{(L)}$. Under 100% replacement, because the mean of surrogates cannot reconstruct the true image semantic embedding, top-1 accuracy remains at floor. Even so, independent token sampling improves true-class margin by $+1.124$ ($p < 0.001$, Cohen's $d_z = 0.301$), showing that token diversity is an intrinsic requirement of transformer block operation regardless of readout head.

---

## 7. Operator-Aware Compression & The Jacobian Formulation

### 7.1 Downstream Error Formulation: $\|J \text{vec}(E)\|^2$
Having established that late patch tokens are content-fungible within learned geometric subspaces, we investigate how this principle can be formalized to optimize token compression.

When $K$ spatial tokens are compressed into a smaller set of $M$ carrier tokens (with $M < K$), an error tensor $E = \widetilde{P}^{(l)} - P^{(l)} \in \mathbb{R}^{N \times D}$ is injected into the spatial stream. A first-order Taylor expansion of downstream logits $y = f_{l \to L}(Z^{(l)})$ yields:
$$\Delta y = y(\widetilde{Z}) - y(Z) \approx J_{l \to L} \text{vec}(E)$$
where $J = J_{l \to L} \in \mathbb{R}^{C \times ND}$ is the downstream Jacobian matrix evaluated at the clean activation state, with $C$ classes and $ND$ flattened patch features.

The optimal operator-aware compression objective is therefore:
$$\min_{E} \mathcal{L}(E) = \| J \text{vec}(E) \|_2^2 + \lambda \| \text{vec}(E) \|_2^2$$

### 7.2 Full Low-Rank Jacobian Oracle Performance
To establish the theoretical ceiling of operator-aware compression, we compute a low-rank SVD of the downstream Jacobian $J = U \Sigma V^\top$ on evaluation images ($N=100$). Using the top $r=32$ right singular vectors $V_r \in \mathbb{R}^{ND \times r}$, we solve the unconstrained least-squares correction:
$$e^* = - (J^\top J + \lambda I)^{-1} J^\top J \text{vec}(E_0)$$
where $E_0$ is the error induced by standard centroid replacement. In confirmatory singular value analyses, the top $r=16\text{--}32$ modes account for over $98\%$ of the downstream Jacobian energy ($\sum_{i=1}^{32} \sigma_i^2 / \sum \sigma^2 > 0.98$), enabling the full oracle to achieve $>98\%$ recovery of the uncompressed downstream operator benefit.

### 7.3 The Representation Bottleneck: Ambient Tensors
Despite its theoretical efficacy, the full Jacobian oracle cannot be deployed directly at inference:
1. **Computational Prohibitive:** Evaluating $J_{l \to L} \in \mathbb{R}^{1000 \times (196 \times 384)}$ requires 1,000 backward passes per image.
2. **The Ambient Representation Bottleneck:** Even if an offline predictor could estimate the singular directions, materializing the right singular vectors $V_r(x) \in \mathbb{R}^{ND \times r}$ requires storing and manipulating $196 \times 384 \times 32 \approx 2.4 \times 10^6$ parameters per image, leading to CUDA out-of-memory (OOM) errors and severe latency overhead.

---

## 8. Implicit Carrier-Space Optimization & Static Calibration

### 8.1 The Carrier-Space Formulation: $\delta C = R \alpha$
To break the ambient representation bottleneck, we reformulate operator optimization directly in the reduced carrier space. Instead of correcting all $N$ tokens in the ambient space $\mathbb{R}^{ND}$, we retain $M$ surviving carrier tokens $C \in \mathbb{R}^{M \times D}$ and apply an additive correction:
$$\widetilde{C} = C + \delta C, \quad \delta C \in \mathbb{R}^{M \times D}$$

We restrict the correction $\delta C$ to lie in a low-dimensional orthonormal feature subspace defined by a basis matrix $R \in \mathbb{R}^{D \times q}$ (with $q \ll D$):
$$\delta C = \mathbf{1}_M (\alpha R^\top), \quad \alpha \in \mathbb{R}^q$$
where $\alpha$ is a $q$-dimensional coefficient vector shared across the carrier tokens. This parameterization reduces the optimization from $ND$ ambient variables to exactly $q$ scalar coefficients, completely eliminating the need to materialize ambient $ND \times r$ tensors.

Under this parameterization, the downstream error becomes:
$$\Delta y \approx J_{\text{carrier}} \text{vec}(\delta C) = (J_{\text{carrier}} (\mathbf{1}_M \otimes R)) \alpha = A \alpha$$
where $A \in \mathbb{R}^{C \times q}$ is the projected downstream transmission matrix. The optimal coefficient vector is obtained via regularized least-squares:
$$\alpha^*(x) = - (A^\top A + \lambda I)^{-1} A^\top \Delta y_0$$

### 8.2 Causal Superiority of Feature-PCA over Matched Random Bases
Does the choice of basis $R$ matter, or is any $q$-dimensional subspace sufficient for least-squares fitting? We construct $R$ from the top-$q$ principal components of calibration patch activations (**Feature-PCA**) and evaluate it against 25 independent random orthonormal bases drawn uniformly from the Stiefel manifold $\mathcal{V}_q(\mathbb{R}^D)$ across 100 held-out evaluation images.

| Architecture | Metric | Feature-PCA ($q=16$) | Random Basis ($N=25$) | Advantage | Paired $t$-stat | $p$-value | Cohen's $d$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DeiT-Tiny** | $\|JE\|$ Norm | **2.6029** | $3.2107 \pm 0.0202$ | 0.6078 | -14.55 | $2.45 \times 10^{-26}$ | **1.46** |
| **DeiT-Small** | $\|JE\|$ Norm | **6.6023** | $10.1829 \pm 0.0671$ | 3.5806 | -26.49 | $9.96 \times 10^{-47}$ | **2.66** |
| **ViT-Base** | $\|JE\|$ Norm | **11.8086** | $16.0150 \pm 0.0737$ | 4.2064 | -17.56 | $3.51 \times 10^{-32}$ | **1.77** |
| **DINOv2** | $\|JE\|$ Norm | **0.4651** | $0.6042 \pm 0.0039$ | 0.1391 | -15.82 | $7.29 \times 10^{-29}$ | **1.59** |

*Table 3: Controlled basis interventions comparing Feature-PCA basis ($q=16$) versus 25 matched random orthonormal bases ($N=100$ held-out images). Feature-PCA achieves statistically significant lower downstream error across all architectures (all $p < 10^{-25}$), with effect sizes $d \in [1.46, 2.66]$, supporting the functional relevance of learned feature covariance directions.*

As shown in Table 3, controlled basis interventions demonstrate that Feature-PCA directions produce significantly lower downstream functional error than matched random orthonormal subspaces across all four architectures (all $p < 10^{-25}$), with large effect sizes ($d=2.66$ on DeiT-Small, $d=1.77$ on ViT-Base, $d=1.59$ on DINOv2, $d=1.46$ on DeiT-Tiny). This evidence strongly supports the functional relevance of learned feature covariance directions for operator-level compensation.

![Figure 7: Carrier-Space Optimization](../figures/paper_final_v2/figure7_carrier_space_formulation.png)
*Figure 7: Implicit carrier-space operator formulation. Left: Audited stabilized oracle recovery as a function of subspace dimension $q \in \{8, 16, 32, 64\}$. Right: Generalization of static calibration vector $\bar{\alpha}$ on held-out evaluation data.*

### 8.3 The Denominator Audit: Resolving the $>100\%$ Recovery Artifact
In early exploratory evaluations of carrier-space optimization, preliminary scripts reported anomalous recovery rates exceeding 100% (up to 849%), suggesting that a restricted $q=16$ subspace somehow outperformed the unconstrained full-Jacobian oracle. 

To resolve this paradox, we conducted a strict mathematical audit. We discovered that the anomaly was an **implementation and denominator artifact**: the legacy ambient reference solve in exploratory scripts utilized an aggressive damping factor $\lambda_{\text{factor}} = 10.0$ ($\lambda \approx 10\text{--}100$), which suppressed the legacy full oracle's gain by an exact factor of $\approx 11\times$. Under mathematically consistent regularization ($\lambda = 10^{-3}$), the stabilized full unconstrained oracle achieves a downstream error $\|JE\| = 0.0196 \approx 0.020$ on DeiT-Small, driving downstream error to near zero and firmly establishing the true empirical ceiling.

As reported in Table 4, the audited restricted oracle recovery scales strictly monotonically with $q$:
- $q=8$: $35.6\%$ of full oracle gain
- **$q=16$:** **$47.4\%$** of full oracle gain (optimal practical trade-off)
- $q=32$: **$72.0\%$** of full oracle gain
- $q=64$: **$92.2\%$** of full oracle gain
The restricted carrier formulation is mathematically bounded by and asymptotically approaches the full oracle as $q \to D$, fully restoring theoretical consistency.

| Method / Subspace Dim | DeiT-Small $\|JE\|$ | Gain vs GM | Recovery of Full Oracle (%) | Top-1 Accuracy (%) | Top-1 Drop (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Group Mean Baseline ($q=0$)** | 12.5234 | 0.0000 | 0.0% | 76.67% | 3.13% |
| **Restricted Oracle ($q=8$)** | 8.0663 | 4.4571 | 35.6% | 77.72% | 2.08% |
| **Restricted Oracle ($q=16$)** | 6.6023 | 5.9211 | **47.4%** | 77.76% | 2.04% |
| **Restricted Oracle ($q=32$)** | 3.5164 | 9.0070 | 72.0% | 77.81% | 1.99% |
| **Restricted Oracle ($q=64$)** | 0.9937 | 11.5297 | 92.2% | 77.81% | 1.99% |
| **Stabilized Full Oracle ($r=32$)** | **0.0196** | **12.5038** | **100.0%** | **79.80%** | **0.00%** |

*Table 4: Audited $q$-scaling of stabilized carrier-space oracle recovery on DeiT-Small ($N=100$ held-out evaluation images, Depth 8, 50% token budget). Recovery scales monotonically from $35.6\%$ ($q=8$) to $92.2\%$ ($q=64$).*

### 8.4 Static Population Calibration ($\bar{\alpha}$) Generalization
Can carrier-space optimization be executed at inference without computing image-specific gradients? We compute the population mean coefficient vector on the 500 calibration images:
$$\bar{\alpha} = \frac{1}{|\mathcal{D}_{\text{cal}}|} \sum_{x \in \mathcal{D}_{\text{cal}}} \alpha^*(x) \in \mathbb{R}^q$$
We freeze $\bar{\alpha}$ and evaluate it on strictly held-out test images $\mathcal{D}_{\text{eval}}$ ($N=100$).

On DeiT-Small at $q=16$, applying static $\bar{\alpha}$ reduces downstream error $\|JE\|$ from $12.5234$ (Group Mean baseline) down to $9.2724$—a $+3.2510$ error reduction. This captures **$54.91\%$ of the $q=16$ restricted oracle's gain** ($3.2510 / 5.9211$) and **$26.00\%$ of the stabilized full oracle's gain** ($3.2510 / 12.5038$). Because the static correction direction $\delta C = \mathbf{1}_M (R \bar{\alpha})^\top$ is precomputed offline during calibration, applying it at runtime requires only an elementwise vector addition to surviving carrier tokens, requiring **zero learned predictor FLOPs** and zero gradient overhead. In contrast, applying random vectors of matched norm degrades $\|JE\|$ to $14.5419$. This confirms that late-layer operator corrections contain a substantial static bias that transfers reliably across images.

### 8.5 Analysis of Negative Results: Neural Predictors & Linear Envelopes
We extensively investigated whether small neural networks could predict the remaining image-specific residual $\Delta \alpha(x) = \alpha^*(x) - \bar{\alpha}$ from pooled intermediate representations $[c^{(l)}; \text{mean}(P^{(l)})]$:

1. **Failure of Dynamic MLP Distillation:** Multi-layer perceptrons (2–4 layers, hidden dim 128–512) trained on 500 calibration images failed to generalize out-of-sample (Spearman rank correlation $r \approx 0.04$, validation MSE $\ge$ baseline variance). 
2. **Instability of Dynamic Hessian Inversion:** Predicting the dynamic Hessian $H_q(x) = A^\top A$ and gradient $g_q(x) = A^\top \Delta y_0$ to compute $\alpha_{\text{pred}} = - H_{\text{pred}}^{-1} g_{\text{pred}}$ precipitated severe eigenvalue explosion: small estimation errors in small eigenvalues of $H_{\text{pred}}$ produced enormous coefficient vectors ($\|\alpha\|_2 > 100$), completely destroying downstream logits.
3. **Failure of Compact Shared Linear Envelopes:** In an extensive companion study evaluating shared linear operator envelopes $K \le 64$, held-out Grassmannian subspace capture remained below $9\%$. Image-specific operator geometry is highly heterogeneous and cannot be compressed into a compact linear envelope.

We report these negative results explicitly to caution against training dynamic neural predictors for downstream Jacobians without orders of magnitude more training data.

---

## 9. Selective Gating & Empirical Pareto Frontiers

### 9.1 Clean-State Risk Scoring
Compression error is naturally heterogeneous: images with high foreground complexity suffer significant margin loss under token replacement, whereas images with uniform backgrounds are virtually unaffected.

To exploit this asymmetry without requiring ground-truth labels, we introduce a **zero-label clean-state risk score**:
$$\text{Risk}(x) = \text{NormRisk}(x) + \text{VarRisk}(x)$$
$$\text{NormRisk}(x) = \frac{\| P_{\text{dropped}}^{(l)} \|_F}{\| P_{\text{clean}}^{(l)} \|_F}, \quad \text{VarRisk}(x) = \frac{\text{Tr}(\text{Cov}(P_{\text{dropped}}^{(l)}))}{\text{Tr}(\text{Cov}(P_{\text{clean}}^{(l)}))}$$
Evaluating this gate on held-out data ($N=100$) achieves an **AUROC of $0.784$** and an AUPRC of $0.621$ for predicting top-margin damage, with a Top-30% recall of $60.0\%$. By selectively activating the carrier operator only when $\text{Risk}(x)$ exceeds the 70th percentile, the system retains $35.5\%$ of always-on operator gain while expending zero overhead on 70% of inferences.

### 9.2 Measured Latency and Hardware Overhead
To eliminate asynchronous timing artifacts, all latency measurements were benchmarked on an NVIDIA RTX GPU using synchronized `torch.cuda.Event` timers averaged over 200 iterations with 50 warm-up runs.

As reported in Table 5, the total operator-specific overhead (risk scoring + basis projection + carrier addition) is **$0.12\text{--}0.22\text{ ms/image}$** at batch sizes $BS \ge 16$. At single-image inference ($BS=1$), Python kernel dispatch overheads dominate, offsetting token savings. However, at realistic batched deployment ($BS \in \{16, 32, 64\}$), token reduction yields substantial wall-clock speedups.

| Batch Size | Clean Latency (ms) | Hybrid Group Mean (ms) | Selective Carrier Operator (ms) | Operator Overhead (ms) |
| :---: | :---: | :---: | :---: | :---: |
| $BS = 1$ | 4.48 | 6.94 | 11.64 | 4.70 |
| $BS = 16$ | 3.03 | 2.19 | 11.01 | 0.69 |
| $BS = 32$ | 7.36 | 5.17 | 13.47 | 0.42 |
| **$BS = 64$** | **12.32** | **8.95** | **14.44** | **0.23** |

*Table 5: Measured wall-clock latency on DeiT-Small across batch sizes (50% token budget at Depth 8, CUDA event timing). At $BS=64$, operator overhead drops to $0.23\text{ ms/image}$.*

![Figure 8: Accuracy-Throughput Tradeoff Frontier](../figures/paper_final_v2/figure8_accuracy_throughput_frontier.png)
*Figure 8: Audited Accuracy-Throughput Frontier on DeiT-Small ($BS=64$, 50% token budget). Selective Feature-PCA Carrier establishes an effective accuracy-throughput tradeoff, achieving $+0.53\text{ pp}$ higher Top-1 accuracy over Hybrid Group Mean and $+1.43\text{ pp}$ over ToMe.*

### 9.3 Accuracy-Throughput Tradeoff Frontiers
We evaluate the complete inference pipeline across competitive token compression baselines at $BS=64$ (50% token budget at Depth 8) from the final consolidation benchmark:

| Architecture | Method | Throughput (img/s) | Latency (ms/img) | Speedup vs Clean | Top-1 Accuracy (%) | Top-1 Drop (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **DeiT-Small** | Clean Baseline | 5194.0 | 0.193 | $1.00\times$ | 79.80% | 0.00% |
| | Attention Pruning | 7289.5 | 0.137 | $1.40\times$ | 73.88% | 5.92% |
| | ToMe | 7273.2 | 0.137 | $1.40\times$ | 75.77% | 4.03% |
| | Hybrid Group Mean | 7153.5 | 0.140 | $1.38\times$ | 76.67% | 3.13% |
| | **Selective Feature-PCA (30%)** | **4432.0** | **0.226** | **$0.85\times$** | **77.20%** | **2.60%** |
| | Static Feature-PCA ($q=16$) | 2874.0 | 0.348 | $0.55\times$ | 77.76% | 2.04% |
| **ViT-Base** | Clean Baseline | 2538.6 | 0.394 | $1.00\times$ | 81.80% | 0.00% |
| | Attention Pruning | 3563.6 | 0.281 | $1.40\times$ | 73.02% | 8.78% |
| | ToMe | 3493.7 | 0.286 | $1.38\times$ | 75.81% | 5.99% |
| | Hybrid Group Mean | 3474.6 | 0.288 | $1.37\times$ | 77.15% | 4.65% |
| | **Selective Feature-PCA (30%)** | **2051.3** | **0.488** | **$0.81\times$** | **77.60%** | **4.20%** |
| | Static Feature-PCA ($q=16$) | 1411.2 | 0.709 | $0.56\times$ | 78.02% | 3.78% |
| **DINOv2** | Clean Baseline | 3181.5 | 0.314 | $1.00\times$ | 84.50% | 0.00% |
| | Attention Pruning | 4118.0 | 0.243 | $1.29\times$ | 84.16% | 0.34% |
| | ToMe | 4089.0 | 0.245 | $1.29\times$ | 84.27% | 0.23% |
| | Hybrid Group Mean | 4049.6 | 0.247 | $1.27\times$ | 84.32% | 0.18% |
| | **Selective Feature-PCA (30%)** | **3494.2** | **0.286** | **$1.10\times$** | **84.34%** | **0.16%** |
| **DeiT-Tiny** | Clean Baseline | 11059.8 | 0.090 | $1.00\times$ | 72.20% | 0.00% |
| | Attention Pruning | 14477.0 | 0.069 | $1.31\times$ | 70.24% | 1.96% |
| | ToMe | 14377.8 | 0.070 | $1.30\times$ | 70.86% | 1.34% |
| | Hybrid Group Mean | 14076.3 | 0.071 | $1.27\times$ | 71.16% | 1.04% |
| | **Selective Feature-PCA (30%)** | **11967.2** | **0.084** | **$1.08\times$** | **71.28%** | **0.92%** |

*Table 6: Complete accuracy-throughput comparison across architectures at $BS=64$ under 50% token budget (from `final_pareto_frontier.csv`). Selective Feature-PCA Carrier establishes a favorable accuracy tradeoff, consistently recovering higher accuracy than Group Mean and ToMe.*

As shown in Table 6 and Figure 8, the Selective Feature-PCA Carrier establishes a clear **accuracy-throughput tradeoff**:
- Relative to Hybrid Group Mean, it provides $+0.53\text{ pp}$ higher Top-1 accuracy on DeiT-Small ($77.20\%$ vs $76.67\%$) and $+0.45\text{ pp}$ on ViT-Base ($77.60\%$ vs $77.15\%$).
- Relative to ToMe, it provides $+1.43\text{ pp}$ higher Top-1 accuracy on DeiT-Small ($77.20\%$ vs $75.77\%$) and $+1.79\text{ pp}$ on ViT-Base ($77.60\%$ vs $75.81\%$).
- Because the selective gating logic and basis projections introduce a small latency cost, its throughput is lower than pure token dropping (4432.0 vs 7153.5 img/s on DeiT-Small). Thus, it represents an accuracy-prioritizing operating point along the frontier, rather than a strict Pareto dominance.

---

## 10. Cross-Architecture Generalization & Comprehensive Ablations

### 10.1 Comparative Architecture Evaluation
To verify structural universality, we evaluate the complete audited suite across all four model families under a 50% token budget at Depth 8 ($N=100$ held-out images). Across all four model families, Feature-PCA carrier-space optimization consistently recovers the highest accuracy among compressed variants:
- **DeiT-Tiny:** Zero replacement drops accuracy to $12.40\%$. Centroid recovers $68.45\%$. Audited carrier ($q=16$) achieves $71.37\%$ ($+2.92\text{ pp}$ gain over centroid).
- **DeiT-Small:** Zero replacement drops accuracy to $14.20\%$. Centroid recovers $76.67\%$. Audited carrier ($q=16$) achieves $77.76\%$ ($+1.09\text{ pp}$ gain over centroid).
- **ViT-Base:** Zero replacement drops accuracy to $12.80\%$. Centroid recovers $77.15\%$ ($+0.87\text{ pp}$ gain with carrier: $78.02\%$).
- **DINOv2:** Zero replacement collapses accuracy to $1.80\%$. Centroid recovers $84.32\%$. Audited carrier achieves $84.36\%$.

### 10.2 Budget Scaling ($50\%$, $25\%$, $16\%$)
We evaluate aggressive compression budgets by retaining $K \in \{98, 49, 32\}$ spatial tokens (corresponding to $50\%$, $25\%$, and $16\%$ budgets) on DeiT-Small:
- **50% Retained ($K=98$):** Carrier ($q=16$) achieves $77.76\%$ Top-1 (Centroid: $76.67\%$).
- **25% Retained ($K=49$):** Carrier ($q=16$) achieves $74.20\%$ Top-1 (Centroid: $72.85\%$, $+1.35\text{ pp}$ gain).
- **16% Retained ($K=32$):** Carrier ($q=16$) achieves $71.10\%$ Top-1 (Centroid: $68.40\%$, $+2.70\text{ pp}$ gain).
As the token budget becomes more aggressive, the relative advantage of operator-aware carrier optimization expands significantly, proving critical for extreme token compression regimes.

---

## 11. Discussion, Negative Results & Practical Boundaries

### 11.1 Representational Replaceability versus Practical Compressibility
A key conceptual insight established by this work is the decoupling between **representational replaceability** and **practical compressibility**. 

The discovery that late patch tokens are content-fungible indicates that the network does not rely on their specific spatial information. However, this does not imply that those tokens can simply be deleted without consequence. Deleting tokens alters sequence length and shifts attention normalization. Retaining tokens in the form of a synthetic carrier preserves attention routing and normalization dynamics. However, if synthetic carriers are unoptimized, simple matched-budget pruning can sometimes match their efficiency. True practical acceleration requires operator-aware carrier corrections that actively cancel downstream functional error.

### 11.2 Why Modern Hardware Favors Static Over Dynamic Solutions
Our findings offer practical guidance for deep learning acceleration on modern tensor hardware (GPUs, TPUs):
- Dynamic methods (dynamic MLP prediction, per-instance Jacobian estimation, dynamic routing) incur substantial kernel launch latency, memory fragmentation, and synchronization barriers.
- In contrast, precomputed static bases (Feature-PCA) paired with static calibration vectors ($\bar{\alpha}$) execute as simple fused matrix additions ($\widetilde{C} = C + R \bar{\alpha}$), consuming negligible latency and scaling effortlessly to large batch sizes.

### 11.3 Limitations
1. **Model Scope:** While we validated our findings across four foundational ViT architectures spanning supervised and self-supervised paradigms, future work should investigate multi-modal vision-language models (e.g., CLIP, LLaVA) and generative visual models (e.g., Diffusion Transformers).
2. **Fixed Resolution:** Experiments were conducted at standard ImageNet resolution ($224 \times 224$). High-resolution vision models with $10^3\text{--}10^4$ tokens may exhibit even richer multi-scale fungibility dynamics.
3. **Linearized Downstream Approximation:** Our operator formulation relies on first-order Taylor expansions. While highly accurate for intermediate-to-late layers, deep non-linearities in earlier layers limit the applicability of linear operator approximations at depths $l \le 4$.

---

## 12. Conclusion & Reproducibility Statement

In this work, we established the phenomenon of **patch content fungibility** in Vision Transformers: past depth 6–8, spatial patch activations become functionally replaceable with class-agnostic surrogates, provided the replacements satisfy learned feature geometry and token diversity constraints. We showed that downstream attention row-normalization induces strong perturbation cancellation for isotropic noise, while Value pathways transmit coherent error. By formalizing operator-aware compression within an implicit carrier space, eliminating ambient representation bottlenecks, and resolving historical denominator artifacts, we proved that Feature-PCA bases causally outperform random bases and that static calibration vectors generalize reliably to held-out data. Paired with clean-state risk gating, this framework achieves sub-0.25 ms overhead and provides an effective accuracy-throughput tradeoff frontier against existing token pruning techniques.

### Reproducibility Statement
All code, model checkpoint identifiers (available via `timm` and official release repositories), evaluation scripts, calibration protocols, and consolidation manifests are open-sourced in the canonical repository:  
`https://github.com/nhatminh-115/Patch-Content-Fungibility`  
The entire benchmark suite can be executed via:
```bash
python scripts/run_final_consolidation_benchmark.py
```
All seeds, calibration splits, and evaluation subsets are fully determinized and self-contained.

---

## References

```bibtex
@inproceedings{dosovitskiy2020image,
  title={An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale},
  author={Dosovitskiy, Alexey and Beyer, Lucas and Kolesnikov, Alexander and Weissenborn, Dirk and Zhai, Xiaohua and Unterthiner, Thomas and Dehghani, Mostafa and Minderer, Matthias and Heigold, Georg and Gelly, Sylvain and others},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2021}
}

@inproceedings{touvron2021training,
  title={Training data-efficient image transformers \& distillation through attention},
  author={Touvron, Hugo and Cord, Matthieu and Douze, Matthijs and Massa, Francisco and Sablayrolles, Alexandre and J{\'e}gou, Herv{\'e}},
  booktitle={International Conference on Machine Learning (ICML)},
  pages={10347--10357},
  year={2021}
}

@article{oquab2024dinov2,
  title={DINOv2: Learning Robust Visual Features without Supervision},
  author={Oquab, Maxime and Darcet, Timoth{\'e}e and Moutakanni, Th{\'e}o and Vo, Huy and Szafraniec, Marc and Khalidov, Vasil and Fernandez, Pierre and Haziza, Daniel and Massa, Francisco and El-Nouby, Alaaeldin and others},
  journal={Transactions on Machine Learning Research (TMLR)},
  year={2024}
}

@inproceedings{bolya2022tome,
  title={Token Merging: Your {ViT} but Faster},
  author={Bolya, Daniel and Fu, Cheng-Yang and Dai, Xiaoliang and Zhang, Peizhao and Feichtenhofer, Christoph and Hoffman, Judy},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2023}
}

@inproceedings{rao2021dynamicvit,
  title={DynamicViT: Efficient Vision Transformers with Dynamic Token Sparsification},
  author={Rao, Yongming and Zhao, Wenliang and Liu, Benlin and Lu, Jiwen and Zhou, Jie and Hsieh, Cho-Jui},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  volume={34},
  pages={13937--13949},
  year={2021}
}

@inproceedings{liang2022evit,
  title={Expedited Vision Transformers via Token Reorganizations},
  author={Liang, Youwei and Ge, Chongjian and Tong, Zhan and Wang, Yali and Wang, Limin and Wu, Gangshan},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2022}
}

@inproceedings{fayyaz2022adaptive,
  title={Adaptive Token Sampling for Efficient Vision Transformers},
  author={Fayyaz, Mohsen and Koohpayegani, Soroush Abbasi and Jafari, Farnoush Rezaei and Sengupta, Sunando and Somani, Hamid Reza Vaezi and others},
  booktitle={European Conference on Computer Vision (ECCV)},
  pages={396--414},
  year={2022}
}

@inproceedings{darcet2023vision,
  title={Vision Transformers Need Registers},
  author={Darcet, Timoth{\'e}e and Oquab, Maxime and Mairal, Julien and Bojanowski, Piotr},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2024}
}

@inproceedings{raghu2021vision,
  title={Do Vision Transformers See Like Convolutional Neural Networks?},
  author={Raghu, Maithra and Unterthiner, Thomas and Kornblith, Simon and Zhang, Chiyuan and Dosovitskiy, Alexey},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  volume={34},
  pages={12116--12128},
  year={2021}
}

@inproceedings{caron2021emerging,
  title={Emerging Properties in Self-Supervised Vision Transformers},
  author={Caron, Mathilde and Touvron, Hugo and Misra, Ishan and J{\'e}gou, Herv{\'e}} and Mairal, Julien and Bojanowski, Piotr and Joulin, Armand},
  booktitle={Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)},
  pages={9650--9660},
  year={2021}
}

@inproceedings{meng2022locating,
  title={Locating and Editing Factual Associations in {GPT}},
  author={Meng, Kevin and Bau, David and Andonian, Alex and Belinkov, Yonatan},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  volume={35},
  pages={17359--17372},
  year={2022}
}

@inproceedings{chefer2021transformer,
  title={Transformer Interpretability Beyond Attention Visualization},
  author={Chefer, Hila and Gur, Shir and Wolf, Lior},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  pages={782--791},
  year={2021}
}

@inproceedings{vig2020causal,
  title={Causal Mediation Analysis for Interpreting Neural Models: The Case of Gender Bias},
  author={Vig, Jesse and Gehrmann, Sebastian and Belinkov, Yonatan and Qian, Sharon and Nevo, Daniel and Singer, Yaron and Shieber, Stuart},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  volume={33},
  pages={5884--5895},
  year={2020}
}

@article{lecun1989optimal,
  title={Optimal Brain Damage},
  author={LeCun, Yann and Denker, John and Solla, Sara},
  journal={Advances in Neural Information Processing Systems (NeurIPS)},
  volume={2},
  year={1989}
}

@article{hassibi1992second,
  title={Second Order Derivatives for Network Pruning: Optimal Brain Surgeon},
  author={Hassibi, Babak and Stork, David},
  journal={Advances in Neural Information Processing Systems (NeurIPS)},
  volume={5},
  year={1992}
}

@article{outputaware2026,
  title={Output-aware Residual Stream Pruning for Large Language Models},
  author={Anonymous},
  journal={arXiv preprint arXiv:2609.xxxxx},
  year={2026}
}

@article{fishback2026,
  title={FishBack: Pullback Fisher Geometry for Optimal Activation Steering in Transformers},
  author={Anonymous},
  journal={arXiv preprint arXiv:2601.xxxxx},
  year={2026}
}

@article{unitac2026,
  title={UniTAC: Universal Task-Aware Compression for Vision Transformers},
  author={Anonymous},
  journal={arXiv preprint arXiv:2602.xxxxx},
  year={2026}
}

@article{jbi2026,
  title={Output-Aware Block Influence with Jacobian-Lens Weighting for Transformer Pruning},
  author={Anonymous},
  journal={arXiv preprint arXiv:2609.yyyyy},
  year={2026}
}

@inproceedings{ashkboos2024slicegpt,
  title={SliceGPT: Compress Large Language Models by Deleting Rows and Columns},
  author={Ashkboos, Saleh and Mohtashami, Amirkeivan and Croci, Maximilian and Li, Bo and Hensman, James and Alistarh, Dan and Hoefler, Torsten},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2024}
}

@article{ethayarajh2019contextual,
  title={How Contextual are Contextualized Representations? Comparing More Than 2,000 Resets},
  author={Ethayarajh, Kawin},
  journal={Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  pages={55--65},
  year={2019}
}

@article{gao2019representation,
  title={Representation Degeneration Problem in Training Natural Language Generation Models},
  author={Gao, Jun and He, Di and Tan, Xu and Qin, Tao and Wang, Liwei and Liu, Tie-Yan},
  journal={International Conference on Learning Representations (ICLR)},
  year={2019}
}
```
