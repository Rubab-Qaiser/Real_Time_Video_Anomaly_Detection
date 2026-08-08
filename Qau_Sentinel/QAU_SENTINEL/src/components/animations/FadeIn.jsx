import { motion } from "framer-motion";

const defaultVariants = {
  hidden: {
    opacity: 0,
    y: 20,
  },

  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.45,
      ease: "easeOut",
    },
  },
};

export default function FadeIn({
  children,
  className = "",
  delay = 0,
  duration = 0.45,
  once = true,
  variants = defaultVariants,
}) {
  const animationVariants =
    variants === defaultVariants
      ? {
          hidden: defaultVariants.hidden,
          visible: {
            ...defaultVariants.visible,
            transition: {
              ...defaultVariants.visible.transition,
              delay,
              duration,
            },
          },
        }
      : variants;

  return (
    <motion.div
      className={className}
      variants={animationVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once }}
    >
      {children}
    </motion.div>
  );
}