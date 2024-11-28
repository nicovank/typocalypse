import re

import libcst as cst
from libcst.metadata import ParentNodeProvider


class AddAnyAnnotationsTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = [ParentNodeProvider]

    def __init__(
        self,
        override_existing_annotations: bool,
        self_argument_name_re: re.Pattern[str],
    ) -> None:
        super().__init__()

        self.override_existing_annotations = override_existing_annotations
        self.self_argument_name_re = self_argument_name_re

        self.level = 0
        self.has_any_import = False

    def leave_ImportFrom(
        self, original: cst.ImportFrom, updated: cst.ImportFrom
    ) -> cst.ImportFrom:
        # Ignore non-top-level imports.
        if self.level > 0 or self.has_any_import:
            return updated

        if updated.module and updated.module.value == "typing":
            # Ignore ImportStar.
            if isinstance(updated.names, cst.ImportStar):
                return updated

            self.has_any_import = True
            for alias in updated.names:
                if alias.name.value == "Any":
                    return updated

            return updated.with_changes(
                names=sorted(
                    [*updated.names, cst.ImportAlias(name=cst.Name("Any"))],
                    key=lambda alias: alias.name.value,
                )
            )

        return updated

    def visit_FunctionDef(self, original: cst.FunctionDef) -> bool:
        self.level += 1
        return True

    def visit_ClassDef(self, original: cst.ClassDef) -> bool:
        self.level += 1
        return True

    def leave_ClassDef(
        self, original: cst.ClassDef, updated: cst.ClassDef
    ) -> cst.ClassDef:
        self.level -= 1
        return updated

    def leave_FunctionDef(
        self, original: cst.FunctionDef, updated: cst.FunctionDef
    ) -> cst.FunctionDef:
        self.level -= 1

        if self.override_existing_annotations or updated.returns is None:
            updated = updated.with_changes(returns=cst.Annotation(cst.Name("Any")))

        params = []
        for param in updated.params.params:
            if not self.override_existing_annotations and param.annotation is not None:
                params.append(param)
                continue

            if len(params) == 0 and self.self_argument_name_re.match(param.name.value):
                params.append(param)
                continue

            params.append(
                param.with_changes(annotation=cst.Annotation(cst.Name("Any")))
            )

        return updated.with_changes(params=updated.params.with_changes(params=params))

    def leave_Module(self, original: cst.Module, updated: cst.Module) -> cst.Module:
        if self.has_any_import:
            return updated

        any_import = cst.SimpleStatementLine(
            body=[
                cst.ImportFrom(
                    module=cst.Name("typing"),
                    names=[cst.ImportAlias(name=cst.Name("Any"))],
                )
            ]
        )

        return updated.with_changes(body=[any_import, *updated.body])


def transform(
    source_code: str,
    override_existing_annotations: bool = False,
    self_argument_name_re: str = "self|cls",
) -> str:
    tree = cst.parse_module(source_code)
    wrapper = cst.MetadataWrapper(tree)
    transformer = AddAnyAnnotationsTransformer(
        override_existing_annotations, re.compile(self_argument_name_re)
    )
    modified_tree = wrapper.visit(transformer)
    return modified_tree.code