#!/usr/bin/env python3
"""
Flask-RESTful API with server-side pagination for the /books endpoint.

The Books resource accepts optional ?page and ?per_page query parameters
and returns a structured JSON response that includes both the requested
items and metadata about the full result set.
"""

from flask import request
from flask_restful import Resource
import os

from config import create_app, db, api
from models import Book, BookSchema

env = os.getenv("FLASK_ENV", "dev")
app = create_app(env)


class Books(Resource):
    def get(self):
        """
        Return a paginated list of books.

        Query Parameters:
            page     (int): Page number to return. Defaults to 1.
            per_page (int): Number of items per page. Defaults to 10, max 100.

        Response shape:
            {
                "page": 1,
                "per_page": 10,
                "total": 500,
                "total_pages": 50,
                "items": [ { "id": 1, "title": "...", ... }, ... ]
            }
        """
        # Step 1: Read query parameters with safe defaults.
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)

        # Guard against nonsensical values.
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 1
        # Cap per_page so one request can't dump the entire table.
        if per_page > 100:
            per_page = 100

        # Step 2: Use SQLAlchemy's .paginate() to fetch only the requested slice.
        #   error_out=False → returns an empty page instead of raising 404
        #   for out-of-range page numbers.
        pagination = Book.query.order_by(Book.id).paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

        # Step 3: Build the structured response with metadata + serialized items.
        return {
            "page":        pagination.page,        # current page number
            "per_page":    pagination.per_page,    # items requested per page
            "total":       pagination.total,       # total records across all pages
            "total_pages": pagination.pages,       # total number of pages
            "items":       [BookSchema().dump(b) for b in pagination.items],
        }, 200


api.add_resource(Books, '/books', endpoint='books')

if __name__ == '__main__':
    app.run(port=5555, debug=True)