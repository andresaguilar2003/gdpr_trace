import argparse
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import T5ForConditionalGeneration, T5Tokenizer


DEFAULT_DATA_DIR = Path("app/services/ai/t5/data/processed")
DEFAULT_MODEL_DIR = Path("app/services/ai/t5/models/gdpr_t5_validator")


def parse_compact_output(text):
    normalized = text.strip().lower()

    if normalized.startswith("valid"):
        return True, True

    if normalized.startswith("invalid"):
        return False, True

    return None, False


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate the fine-tuned GDPR T5 validator on test JSONL."
    )
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--model-dir", default=str(DEFAULT_MODEL_DIR))
    parser.add_argument("--max-input-length", type=int, default=512)
    parser.add_argument("--max-target-length", type=int, default=256)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    dataset = load_dataset(
        "json",
        data_files={"test": str(Path(args.data_dir) / "test.jsonl")}
    )["test"]

    if args.limit:
        dataset = dataset.select(range(min(args.limit, len(dataset))))

    tokenizer = T5Tokenizer.from_pretrained(args.model_dir)
    model = T5ForConditionalGeneration.from_pretrained(args.model_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    parseable_outputs = 0
    valid_flag_matches = 0

    for record in dataset:
        inputs = tokenizer(
            record["input_text"],
            return_tensors="pt",
            truncation=True,
            max_length=args.max_input_length
        ).to(device)

        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_length=args.max_target_length,
                do_sample=False
            )

        prediction = tokenizer.decode(
            output_ids[0],
            skip_special_tokens=True
        )

        predicted_validity, is_parseable = parse_compact_output(prediction)
        target_validity, _ = parse_compact_output(record["target_text"])

        if is_parseable:
            parseable_outputs += 1

        if predicted_validity == target_validity:
            valid_flag_matches += 1

    total = len(dataset)

    print(f"Examples: {total}")
    print(f"Parseable outputs: {parseable_outputs}/{total}")
    print(f"isValid matches: {valid_flag_matches}/{total}")


if __name__ == "__main__":
    main()
