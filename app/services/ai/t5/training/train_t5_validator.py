import argparse
from pathlib import Path

from datasets import load_dataset
from transformers import (
    DataCollatorForSeq2Seq,
    T5ForConditionalGeneration,
    T5Tokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments
)


DEFAULT_DATA_DIR = Path("app/services/ai/t5/data/processed")
DEFAULT_OUTPUT_DIR = Path("app/services/ai/t5/models/gdpr_t5_validator")


def tokenize_dataset(dataset, tokenizer, max_input_length, max_target_length):
    def tokenize(batch):
        model_inputs = tokenizer(
            batch["input_text"],
            max_length=max_input_length,
            truncation=True
        )

        labels = tokenizer(
            text_target=batch["target_text"],
            max_length=max_target_length,
            truncation=True
        )

        model_inputs["labels"] = labels["input_ids"]

        return model_inputs

    return dataset.map(
        tokenize,
        batched=True,
        remove_columns=dataset["train"].column_names
    )


def main():
    parser = argparse.ArgumentParser(
        description="Fine-tune t5-small as a GDPR enrichment validator."
    )
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--model-name", default="t5-small")
    parser.add_argument("--epochs", type=float, default=5)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--max-input-length", type=int, default=512)
    parser.add_argument("--max-target-length", type=int, default=256)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)

    dataset = load_dataset(
        "json",
        data_files={
            "train": str(data_dir / "train.jsonl"),
            "validation": str(data_dir / "validation.jsonl")
        }
    )

    tokenizer = T5Tokenizer.from_pretrained(args.model_name)
    model = T5ForConditionalGeneration.from_pretrained(args.model_name)

    tokenized = tokenize_dataset(
        dataset,
        tokenizer,
        max_input_length=args.max_input_length,
        max_target_length=args.max_target_length
    )

    training_args = Seq2SeqTrainingArguments(
        output_dir=str(output_dir),
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
        logging_steps=10,
        save_total_limit=2,
        report_to="none"
    )

    collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        processing_class=tokenizer,
        data_collator=collator
    )

    trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    print(f"Model written to {output_dir}")


if __name__ == "__main__":
    main()
