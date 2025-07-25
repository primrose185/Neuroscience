<script setup lang="ts">
// Page metadata for search indexing
const pageMetadata = {
  id: 'topic1-page1',
  title: 'Probability Theory Fundamentals',
  content: 'Comprehensive introduction to probability theory covering basic concepts, conditional probability, Bayes theorem, and advanced statistical inference. This section provides a complete foundation in probability theory for mathematical and scientific applications.',
  excerpt: 'Complete guide to probability theory from basic concepts to advanced applications.',
  path: '/topic1/page1',
  tags: ['probability', 'mathematics', 'statistics', 'bayes', 'conditional-probability', 'statistical-inference'],
  category: 'Mathematics',
  type: 'page' as const,
  metadata: {
    chapter: 'Chapter 1',
    difficulty: 'beginner' as const,
    estimatedReadTime: 12
  }
}

// Export metadata for search indexing
if (typeof window !== 'undefined') {
  (window as any).__pageMetadata = pageMetadata
}
</script>

<template>
  <div class="page-container p-8">
    <div class="max-w-4xl mx-auto">
      <div class="text-sm text-gray-600 mb-2">Chapter 1</div>
      <h1 class="text-4xl font-bold mb-6">Probability Theory Fundamentals</h1>
      <p class="text-xl text-gray-700 mb-8">
        A comprehensive exploration of probability theory from basic concepts to advanced applications.
      </p>
      
      <!-- Section: Basic Probability ---->
      <section id="basic-probability" class="mb-16">
        <div class="image-container bg-gray-300 rounded-lg h-64 w-full mb-8 shadow-lg flex items-center justify-center">
          <span class="text-gray-500">Probability Distribution Visualization</span>
        </div>
        <div class="content">
          <h2 class="text-3xl font-bold mb-6">Basic Probability</h2>
          <p class="text-lg leading-relaxed mb-6">
            Randomness is all around us. Probability theory is the mathematical framework that allows us 
            to analyze chance events in a logically sound manner. The probability of an event is a number 
            indicating how likely that event will occur. This number is always between 0 and 1, where 0 
            indicates impossibility and 1 indicates certainty.
          </p>
          
          <div class="bg-blue-50 rounded-lg p-6 mb-6">
            <h3 class="text-xl font-semibold mb-4">Fundamental Concepts</h3>
            <ul class="list-disc list-inside space-y-2 text-base">
              <li>Sample space: The set of all possible outcomes</li>
              <li>Events: Subsets of the sample space</li>
              <li>Probability measure: A function assigning probabilities to events</li>
              <li>Probability axioms: The foundational rules of probability</li>
            </ul>
          </div>

          <div class="bg-gray-50 rounded-lg p-6 mb-8">
            <h3 class="text-xl font-semibold mb-4">Basic Probability Formula</h3>
            <p class="text-lg mb-4">The mathematical expression for probability can be written as:</p>
            <div class="flex justify-center">
              <div class="bg-white px-8 py-4 rounded shadow-sm">
                P(E) = n(E) / n(S)
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Section: Conditional Probability ---->
      <section id="conditional-probability" class="mb-16">
        <div class="image-container bg-gray-300 rounded-lg h-64 w-full mb-8 shadow-lg flex items-center justify-center">
          <span class="text-gray-500">Conditional Probability Tree Diagram</span>
        </div>
        <div class="content">
          <h2 class="text-3xl font-bold mb-6">Conditional Probability</h2>
          <p class="text-lg leading-relaxed mb-6">
            Conditional probability measures the likelihood of an event occurring given that another event has already occurred.
            This concept is fundamental to understanding statistical relationships and dependencies between events.
          </p>
          
          <div class="bg-green-50 rounded-lg p-6 mb-6">
            <h3 class="text-xl font-semibold mb-4">Key Properties</h3>
            <ul class="list-disc list-inside space-y-2 text-base">
              <li>Conditional probabilities must satisfy the same axioms as regular probabilities</li>
              <li>The conditioning event must have positive probability</li>
              <li>Independence can be defined through conditional probability</li>
              <li>Chain rule allows decomposition of complex events</li>
            </ul>
          </div>

          <div class="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 class="text-xl font-semibold mb-4">Conditional Probability Formula</h3>
            <p class="text-base leading-relaxed mb-4">
              The probability of event A given that event B has occurred:
            </p>
            <div class="flex justify-center">
              <div class="bg-white px-6 py-3 rounded shadow-sm">
                P(A|B) = P(A ∩ B) / P(B)
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Section: Bayes' Theorem ---->
      <section id="bayes-theorem" class="mb-16">
        <div class="image-container bg-gray-300 rounded-lg h-64 w-full mb-8 shadow-lg flex items-center justify-center">
          <span class="text-gray-500">Bayesian Inference Diagram</span>
        </div>
        <div class="content">
          <h2 class="text-3xl font-bold mb-6">Bayes' Theorem</h2>
          <p class="text-lg leading-relaxed mb-6">
            Bayes' theorem describes the probability of an event based on prior knowledge of conditions 
            that might be related to the event. It provides a mathematical framework for updating beliefs 
            or hypotheses based on new evidence.
          </p>
          
          <div class="bg-purple-50 rounded-lg p-6 mb-6">
            <h3 class="text-xl font-semibold mb-4">Applications</h3>
            <ul class="list-disc list-inside space-y-2 text-base">
              <li>Medical diagnosis and screening tests</li>
              <li>Machine learning and pattern recognition</li>
              <li>Quality control and reliability analysis</li>
              <li>Information theory and signal processing</li>
            </ul>
          </div>

          <div class="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 class="text-xl font-semibold mb-4">Bayes' Theorem Formula</h3>
            <p class="text-base leading-relaxed mb-4">
              The posterior probability of hypothesis A given evidence B:
            </p>
            <div class="flex justify-center">
              <div class="bg-white px-6 py-3 rounded shadow-sm">
                P(A|B) = P(B|A) × P(A) / P(B)
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Section: Statistical Inference ---->
      <section id="statistical-inference" class="mb-16">
        <div class="image-container bg-gray-300 rounded-lg h-64 w-full mb-8 shadow-lg flex items-center justify-center">
          <span class="text-gray-500">Statistical Distribution Models</span>
        </div>
        <div class="content">
          <h2 class="text-3xl font-bold mb-6">Statistical Inference</h2>
          <p class="text-lg leading-relaxed mb-6">
            Statistical inference uses probability theory to draw conclusions about populations based on sample data.
            It provides methods for hypothesis testing, parameter estimation, and quantifying uncertainty in our conclusions.
          </p>
          
          <div class="bg-orange-50 rounded-lg p-6 mb-6">
            <h3 class="text-xl font-semibold mb-4">Inference Methods</h3>
            <ul class="list-disc list-inside space-y-2 text-base">
              <li>Point estimation: Finding single best estimates of parameters</li>
              <li>Interval estimation: Constructing confidence intervals</li>
              <li>Hypothesis testing: Making decisions based on sample evidence</li>
              <li>Bayesian inference: Incorporating prior knowledge</li>
            </ul>
          </div>
          
          <p class="text-lg leading-relaxed">
            These advanced concepts build upon basic probability theory to provide powerful tools for 
            data analysis, scientific research, and decision making under uncertainty.
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  min-height: calc(100vh - 4rem);
}
</style>