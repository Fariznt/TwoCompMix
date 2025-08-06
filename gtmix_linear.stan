functions {

}
data {
  int<lower=1> N;                 // Number of data points
  int<lower=1> M;                 // Number of response variables
  matrix[N, M] y_all;             // Matrix of M response variables
  array[M] int<lower=1> K_per_m;  // Array of predictor counts for each response
  int<lower=1> K_sum;             // Sum of all values in K; total predictor count
  matrix[N, K_sum] X_all;        // All predictor matrices combined column-wise
}

transformed data {

}

parameters {
  real<lower=0, upper=1> theta;  // Mixture weight for the first component
  vector[M] mu1;                 // Means of the first component
  vector[M] mu2;                 // Means of the second component
  vector<lower=0>[M] sigma1;     // Standard deviations of the first component
  vector<lower=0>[M] sigma2;     // Standard deviations of the second component
  vector[K_sum] beta1_flat;      // Regression coefficients for the first component
  vector[K_sum] beta2_flat;      // Regression coefficients for the second component
}
model {
  // Priors
  mu1 ~ 
normal(0,5)
;
  mu2 ~ 
normal(0,5)
;
  sigma1 ~ 
cauchy(0,2.5)
;
  sigma2 ~ 
cauchy(0,2.5)
;
  beta1_flat ~
normal(0,5)
;
  beta2_flat ~
normal(0,5)
;
  theta ~ 
beta(1,1)
;

  // Mixture model likelihood
  for (n in 1:N) {
    real log_prob_comp1 = log(theta);
    real log_prob_comp2 = log1m(theta);
    int current_pos = 1;
    for (m in 1:M) {
      row_vector[K_per_m[m]] X_n_m = X_all[n, current_pos:(current_pos + K_per_m[m] - 1)];
      vector[K_per_m[m]] beta1_m = beta1_flat[current_pos:(current_pos + K_per_m[m] - 1)];
      vector[K_per_m[m]] beta2_m = beta2_flat[current_pos:(current_pos + K_per_m[m] - 1)];
      log_prob_comp1 += normal_lpdf(y_all[n, m] | mu1[m] + X_n_m * beta1_m, sigma1[m]);
      log_prob_comp2 += normal_lpdf(y_all[n, m] | mu2[m] + X_n_m * beta2_m, sigma2[m]);
      current_pos += K_per_m[m];
    }
    target += log_sum_exp(log_prob_comp1, log_prob_comp2);
  }
}
generated quantities {
  int<lower=1, upper=2> z[N];
  for (n in 1:N) {
    real log_prob1 = log(theta);
    real log_prob2 = log1m(theta);
    int current_pos = 1;
    for (m in 1:M) {
      row_vector[K_per_m[m]] X_n_m = X_all[n, current_pos:(current_pos + K_per_m[m] - 1)];
      vector[K_per_m[m]] beta1_m = beta1_flat[current_pos:(current_pos + K_per_m[m] - 1)];
      vector[K_per_m[m]] beta2_m = beta2_flat[current_pos:(current_pos + K_per_m[m] - 1)];
      log_prob1 += normal_lpdf(y_all[n, m] | mu1[m] + X_n_m * beta1_m, sigma1[m]);
      log_prob2 += normal_lpdf(y_all[n, m] | mu2[m] + X_n_m * beta2_m, sigma2[m]);
      current_pos += K_per_m[m];
    }
    vector[2] log_probs;
    log_probs[1] = log_prob1;
    log_probs[2] = log_prob2;
    vector[2] prob = softmax(log_probs);
    z[n] = categorical_rng(prob);
  }
}
