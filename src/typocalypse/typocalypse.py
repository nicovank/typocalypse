import re

import libcst as cst


class AddAnyAnnotationsTransformer(cst.CSTTransformer):
    def __init__(
        self,
        override_existing: bool,
        self_argument_name_re: re.Pattern[str],
    ) -> None:
        super().__init__()

        self.override_existing = override_existing
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

        if self.override_existing or not updated.returns:
            updated = updated.with_changes(returns=cst.Annotation(cst.Name("Any")))

        params = []
        for param in updated.params.params:
            if not self.override_existing and param.annotation:
                params.append(param)
                continue

            if len(params) == 0 and self.self_argument_name_re.match(param.name.value):
                params.append(param)
                continue

            params.append(
                param.with_changes(annotation=cst.Annotation(cst.Name("Any")))
            )

        kwonly_params = []
        for kwonly_param in updated.params.kwonly_params:
            if not self.override_existing and kwonly_param.annotation:
                kwonly_params.append(kwonly_param)
                continue

            kwonly_params.append(
                kwonly_param.with_changes(annotation=cst.Annotation(cst.Name("Any")))
            )

        star_arg = updated.params.star_arg
        if (
            star_arg
            # When only **kwargs is present, star_arg seems to always be set to this value.
            and not isinstance(star_arg, cst.MaybeSentinel)
            and not isinstance(star_arg, cst.ParamStar)
            and (self.override_existing or not star_arg.annotation)
        ):
            star_arg = star_arg.with_changes(annotation=cst.Annotation(cst.Name("Any")))

        star_kwarg = updated.params.star_kwarg
        if star_kwarg and (self.override_existing or not star_kwarg.annotation):
            star_kwarg = star_kwarg.with_changes(
                annotation=cst.Annotation(cst.Name("Any"))
            )

        return updated.with_changes(
            params=updated.params.with_changes(
                params=params,
                kwonly_params=kwonly_params,
                star_arg=star_arg,
                star_kwarg=star_kwarg,
            )
        )

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
    override_existing: bool = False,
    self_argument_name_re: str = "self|cls",
) -> str:
    tree = cst.parse_module(source_code)
    transformer = AddAnyAnnotationsTransformer(
        override_existing, re.compile(self_argument_name_re)
    )
    modified_tree = tree.visit(transformer)
    return modified_tree.code
