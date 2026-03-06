"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Star, X } from "lucide-react";

interface RatingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (rating: number) => void;
}

export function RatingModal({ isOpen, onClose, onSubmit }: RatingModalProps) {
  const [rating, setRating] = useState(0);
  const [hoveredStar, setHoveredStar] = useState(0);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    if (rating < 1) return;
    setSubmitted(true);
    onSubmit(rating);
    setTimeout(() => {
      setSubmitted(false);
      setRating(0);
      onClose();
    }, 2000);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      >
        <motion.div
          initial={{ scale: 0.85, opacity: 0, y: 30 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.85, opacity: 0, y: 30 }}
          transition={{ type: "spring", damping: 20, stiffness: 300 }}
          className="bg-zinc-900 border border-zinc-800 rounded-3xl p-8 w-[90%] max-w-sm text-center relative shadow-2xl"
        >
          {/* Close button */}
          {!submitted && (
            <button
              onClick={onClose}
              className="absolute top-4 right-4 p-1.5 rounded-full text-zinc-500 hover:text-white hover:bg-zinc-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          {submitted ? (
            /* ── Thank You State ── */
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="space-y-4 py-4"
            >
              <motion.div
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ duration: 0.5 }}
                className="text-5xl"
              >
                🎉
              </motion.div>
              <h3 className="text-2xl font-bold text-white">Thank you!</h3>
              <p className="text-zinc-400 text-sm">
                We appreciate your feedback.
              </p>
            </motion.div>
          ) : (
            /* ── Rating State ── */
            <div className="space-y-6">
              <div className="space-y-2">
                <h3 className="text-2xl font-bold text-white">
                  Rate your experience
                </h3>
                <p className="text-zinc-400 text-sm">
                  How was your shopping assistance today?
                </p>
              </div>

              {/* Stars */}
              <div className="flex justify-center gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setRating(star)}
                    onMouseEnter={() => setHoveredStar(star)}
                    onMouseLeave={() => setHoveredStar(0)}
                    className="p-1 transition-transform hover:scale-125 active:scale-95"
                  >
                    <Star
                      className={`w-10 h-10 transition-colors duration-150 ${
                        star <= (hoveredStar || rating)
                          ? "fill-yellow-400 text-yellow-400"
                          : "text-zinc-700"
                      }`}
                    />
                  </button>
                ))}
              </div>

              {/* Rating label */}
              <p className="text-sm text-zinc-500 h-5">
                {rating === 1
                  ? "Poor"
                  : rating === 2
                  ? "Fair"
                  : rating === 3
                  ? "Good"
                  : rating === 4
                  ? "Great"
                  : rating === 5
                  ? "Excellent!"
                  : ""}
              </p>

              {/* Submit */}
              <button
                onClick={handleSubmit}
                disabled={rating < 1}
                className="w-full py-3 rounded-2xl font-semibold text-sm bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-[0.98]"
              >
                Submit Rating
              </button>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
