<template>
  <section class="workflow-frame" :style="{ '--step': step }">
    <div class="workflow-frame-copy">
      <span class="workflow-frame-kicker">Flux {{ String(step).padStart(2, '0') }} · {{ eyebrow }}</span>
      <h2>{{ title }}</h2>
      <p>{{ description }}</p>
    </div>

    <div class="workflow-tracker" aria-label="Progression du flux de production">
      <template v-for="(item, index) in stages" :key="item.short">
        <span class="workflow-tracker-step" :class="{ done: index + 1 < step, active: index + 1 === step }">
          <b>{{ index + 1 }}</b><em>{{ item.short }}</em>
        </span>
        <span v-if="index < stages.length - 1" class="workflow-tracker-line" :class="{ done: index + 1 < step }"></span>
      </template>
    </div>

    <div v-if="$slots.meta" class="workflow-frame-meta"><slot name="meta" /></div>
  </section>
</template>

<script setup>
defineProps({
  step: { type: Number, required: true },
  eyebrow: { type: String, required: true },
  title: { type: String, required: true },
  description: { type: String, required: true },
})

const stages = [
  { short: 'Réception' },
  { short: 'Tri' },
  { short: 'Séchage' },
  { short: 'Condition.' },
  { short: 'Stock' },
]
</script>

<style scoped>
.workflow-frame {
  display: grid; grid-template-columns: minmax(230px, 1.2fr) minmax(370px, 1fr) auto; align-items: center; gap: 24px;
  margin: -6px 0 24px; padding: 19px 22px; border: 1px solid rgba(22,91,61,0.14); border-radius: var(--radius-lg);
  background: linear-gradient(100deg, rgba(255,255,255,0.93), rgba(244,251,231,0.86)); box-shadow: var(--shadow-sm);
}
.workflow-frame-kicker { display: block; color: var(--primary); font-size: 9px; font-weight: 800; letter-spacing: 0.13em; }
.workflow-frame h2 { margin: 3px 0 3px; font-size: 21px; }
.workflow-frame p { max-width: 430px; color: var(--text-secondary); font-size: 11px; line-height: 1.55; }
.workflow-tracker { display: flex; align-items: flex-start; justify-content: center; }
.workflow-tracker-step { display: flex; flex-direction: column; align-items: center; gap: 5px; min-width: 40px; color: var(--text-muted); }
.workflow-tracker-step b { width: 24px; height: 24px; display: grid; place-items: center; border: 1px solid var(--border); border-radius: 50%; background: white; font-size: 10px; }
.workflow-tracker-step em { font-style: normal; font-size: 8px; font-weight: 700; white-space: nowrap; }
.workflow-tracker-step.done, .workflow-tracker-step.active { color: var(--primary); }
.workflow-tracker-step.done b { background: var(--primary); color: white; border-color: var(--primary); }
.workflow-tracker-step.active b { background: var(--lime); color: var(--secondary); border-color: var(--lime); box-shadow: 0 0 0 4px rgba(198,238,140,0.28); }
.workflow-tracker-line { width: clamp(15px, 3.4vw, 44px); height: 1px; margin-top: 12px; background: var(--border); }
.workflow-tracker-line.done { background: var(--primary); }
.workflow-frame-meta { min-width: 112px; padding: 10px 12px; border-radius: 12px; background: var(--secondary); color: white; }
@media (max-width: 1100px) { .workflow-frame { grid-template-columns: 1fr auto; } .workflow-tracker { grid-column: 1 / -1; grid-row: 2; justify-content: flex-start; } }
@media (max-width: 640px) { .workflow-frame { display: block; padding: 18px; } .workflow-tracker { margin-top: 18px; overflow-x: auto; justify-content: flex-start; } .workflow-frame-meta { display: inline-block; margin-top: 12px; } }
</style>
